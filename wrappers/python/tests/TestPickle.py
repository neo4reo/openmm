import unittest
from validateConstraints import *
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
import simtk.openmm
import simtk.openmm.app.element as elem
import simtk.openmm.app.forcefield as forcefield
import copy
import pickle

class TestPickle(unittest.TestCase):
    """Pickling / deepcopy of OpenMM objects."""

    def setUp(self):
        """Set up the tests by loading the input pdb files and force field
        xml files.

        """
        # alanine dipeptide with explicit water
        self.pdb1 = PDBFile('systems/alanine-dipeptide-explicit.pdb')
        self.forcefield1 = ForceField('amber99sb.xml', 'tip3p.xml')
        self.topology1 = self.pdb1.topology
        self.topology1.setUnitCellDimensions(Vec3(2, 2, 2))

        # alalnine dipeptide with implicit water
        self.pdb2 = PDBFile('systems/alanine-dipeptide-implicit.pdb')
        self.forcefield2 = ForceField('amber99sb.xml', 'amber99_obc.xml')

    def test_force_deepcopy(self):
        """Test that deep copying of forces works correctly."""
        force = NonbondedForce()
        force_copy = copy.deepcopy(force)
        # Check class name is same.
        self.assertEqual(force.__class__.__name__, force_copy.__class__.__name__)
        # Check Force object contents are the same.
        self.assertEqual(XmlSerializer.serialize(force), XmlSerializer.serialize(force_copy))

    def test_deepcopy(self):
        """Test that serialization/deserialization works (via deepcopy)."""

        system = self.forcefield1.createSystem(self.pdb1.topology)
        integrator = VerletIntegrator(2*femtosecond)
        context = Context(system, integrator)
        context.setPositions(self.pdb1.positions)
        state = context.getState(getPositions=True, getForces=True, getEnergy=True)

        system2 = copy.deepcopy(system)
        integrator2 = copy.deepcopy(integrator)
        state2 = copy.deepcopy(state)

        str_state = pickle.dumps(state)
        str_integrator = pickle.dumps(integrator)

        state3 = pickle.loads(str_state)
        context.setState(state3)

        del context, integrator

        # Check deep copy of each force.
        forces = [ system.getForce(index) for index in range(system.getNumForces()) ]
        for force in forces:
            force_copy = copy.deepcopy(force)
            # Check class name is same.
            self.assertEqual(force.__class__.__name__, force_copy.__class__.__name__)
            # Check Force object contents are the same.
            self.assertEqual(XmlSerializer.serialize(force), XmlSerializer.serialize(force_copy))

if __name__ == '__main__':
    unittest.main()

