"""Read-only local load QA; actual CURRENT OpenSees solves, no base writes."""
import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from analysis.opensees import local_scenarios as local, run_cases as solver


def response(result):
    return ([x for n in result["nodes"] for x in n["displacement"]]
            + [x for r in result["support_reactions"] for x in r["reaction"]]
            + [r["local_end_forces"][end][k] for r in result["elements"] for end in ("i", "j") for k in local.FORCE_COMPONENTS])


class LocalScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = local.fingerprint()
        cls.master = local.read(ROOT / "model/model_master.json")
        cls.loads = local.read(ROOT / "model/loads.json")
        cls.settings = local.read(ROOT / "config/analysis_settings.json")
        cls.sections = {r["section_id"]: r for r in local.read(ROOT / "model/sections.json")["sections"]}
        cls.materials = {r["material_id"]: r for r in local.read(ROOT / "model/materials.json")["materials"]}
        cls.partition = local.FrozenTributaries(cls.master, cls.loads, cls.settings, "EDIFICIO_1", "P2")
        cls.demo = dict(scenario_id="demo", building="EDIFICIO_1", floor="P2", rectangle_xy=[45, 4, 52, 9],
                        mode="persons", persons=10, mass_per_person_kg=68)

    @classmethod
    def tearDownClass(cls):
        assert local.fingerprint() == cls.before, "BASE files changed!"

    def test_inputs_and_units(self):
        a = self.partition.distribute(self.demo)
        self.assertAlmostEqual(a["force_N"], 6670.8)
        self.assertAlmostEqual(a["effective_area_m2"], 35)
        self.assertGreater(len(a["receivers"]), 1)
        mass = self.partition.distribute(self.demo | dict(mode="mass", total_mass_kg=680))
        surface = self.partition.distribute(self.demo | dict(mode="surface", q_local_kN_m2=6670.8/35000))
        self.assertEqual(a["nodal_loads"], mass["nodal_loads"])
        for x,y in zip(a["nodal_loads"], surface["nodal_loads"]): self.assertAlmostEqual(x["Fz_N"], y["Fz_N"])
        for value in (-1, float("nan"), float("inf"), 1.5):
            with self.assertRaises(ValueError): self.partition.distribute(self.demo | dict(persons=value))
        for mode, key in (("persons", "mass_per_person_kg"), ("mass", "total_mass_kg"), ("surface", "q_local_kN_m2")):
            for value in (-1, float("nan"), float("inf")):
                with self.assertRaises(ValueError): self.partition.distribute(self.demo | {"mode":mode,key:value})

    def test_clip_and_holes(self):
        bounds = self.partition.surface.bounds
        a = self.partition.distribute(self.demo | dict(rectangle_xy=[bounds[0]-2, bounds[1]-2, bounds[0]+3, bounds[1]+3]))
        self.assertLess(a["effective_area_m2"], a["drawn_area_m2"])
        for poly in ([self.partition.surface] if self.partition.surface.geom_type == "Polygon" else self.partition.surface.geoms):
            for hole in poly.interiors:
                center = local.Polygon(hole).representative_point()
                with self.assertRaises(ValueError):
                    self.partition.distribute(self.demo | dict(rectangle_xy=[center.x-.05,center.y-.05,center.x+.05,center.y+.05]))
        for rect in ([0,0,0,0],[-100,-100,-90,-90],[0,0,float('inf'),1]):
            with self.assertRaises(ValueError): self.partition.distribute(self.demo | dict(rectangle_xy=rect))

    def test_partition_all_available_floors(self):
        floors = sorted({(r["building"],r["floor"]) for r in self.master["elements"] if r.get("active") and r["type"]=="slab"})
        for building, floor in floors:
            p = local.FrozenTributaries(self.master,self.loads,self.settings,building,floor)
            self.assertTrue(p.verified_panels)

    def test_conservation_equilibrium_linearity_zero_and_explicit(self):
        solved = []
        for n in (0,1,10,20):
            a = self.partition.distribute(self.demo | dict(persons=n))
            self.assertAlmostEqual(sum(r["force_N"] for r in a["receivers"]),a["force_N"],places=6)
            self.assertAlmostEqual(-sum(r["Fz_N"] for r in a["nodal_loads"]),a["force_N"],places=6)
            result, viewer = local.solve_local(self.master,self.loads,self.sections,self.materials,a)
            self.assertEqual(result["qa"]["equilibrium_status"],"PASS")
            self.assertAlmostEqual(result["qa"]["reaction_force_N"][2],a["force_N"],places=5)
            self.assertEqual(len(viewer["elements"]),len(local.read(ROOT/'results/G/result.json')["elements"]))
            solved.append(response(result))
            print(json.dumps(dict(persons=n,force_N=a["force_N"],area_m2=a["effective_area_m2"],receivers=len(a["receivers"]),qa=result["qa"])))
            # The other building is structurally independent; local ED1 gravity
            # must not manufacture an ED2 response.
            self.assertLess(max(abs(x) for r in result["elements"] if r["element_id"].startswith('E2-')
                                for end in ('i','j') for x in r["local_end_forces"][end].values()),1e-7)
        self.assertLess(max(map(abs,solved[0])),1e-8)
        for multiplier, actual in ((10,solved[2]),(20,solved[3])):
            self.assertLess(max(abs(b-multiplier*a) for a,b in zip(solved[1],actual)),1e-6)
        # Independent explicit R+Q_LOCAL run versus the sum of stored bases.
        coefficients = dict(G=1.0,Q=.5,EX=.2,EY=-.1)
        contract = solver.prepare_contract(self.master,self.sections,self.materials,self.loads)
        nodal = {tag:[0.,0.,0.] for tag in contract["used_nodes"]}
        for case,factor in coefficients.items():
            if case in ('G','Q'):
                for tag,fz in contract['nodal'][case].items(): nodal[tag][2]+=factor*fz
            else:
                axis=0 if case=='EX' else 1
                for tag, f in contract['lateral'].items():nodal[tag][axis]+=factor*f
        for r in self.partition.distribute(self.demo)['nodal_loads']:
            nodal[contract['tag_to_retained'][r['node_tag']]][2]+=r['Fz_N']
        contract['combined_nodal_loads']=nodal
        explicit=response(solver.run_case(contract,'R'))
        expected=solved[2][:]
        for case,factor in coefficients.items():
            base=response(local.read(ROOT/f'results/{case}/result.json'))
            expected=[x+factor*y for x,y in zip(expected,base)]
        self.assertLess(max(abs(a-b) for a,b in zip(explicit,expected)),1e-4)

    def test_hash_gate(self):
        with self.assertRaises(ValueError): local.execute(self.demo | dict(base_sha256='obsolete'))


if __name__ == '__main__': unittest.main(verbosity=2)
