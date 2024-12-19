# tests/test_calculations.py

import pytest
import uuid
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.calculation import (
    Base,
    User,
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Modulus
)


# Configure a SQLite in-memory database for testing
DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope='module')
def engine():
    """Create a SQLAlchemy engine for the tests."""
    return create_engine(DATABASE_URL, echo=False)


@pytest.fixture(scope='module')
def tables(engine):
    """Create all tables."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def session(engine, tables):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = scoped_session(sessionmaker(bind=connection))
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def test_user_creation(session):
    """Test creating a User."""
    user = User(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        username="johndoe",
        password="hashed_password"
    )
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(email="john.doe@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.first_name == "John"
    assert retrieved_user.last_name == "Doe"
    assert retrieved_user.username == "johndoe"
    assert retrieved_user.password == "hashed_password"
    assert isinstance(retrieved_user.id, uuid.UUID)
    assert isinstance(retrieved_user.created_at, datetime)
    assert isinstance(retrieved_user.updated_at, datetime)


def test_calculation_creation(session):
    """Test creating different Calculation types via the factory."""
    user = User(
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@example.com",
        username="alicesmith",
        password="hashed_password"
    )
    session.add(user)
    session.commit()

    # Define calculation types and inputs
    calc_types = {
        'addition': [1, 2, 3],
        'subtraction': [10, 5, 2],
        'multiplication': [2, 3, 4],
        'division': [20, 5, 2],
        'power': [2, 3],
        'modulus': [10, 3]
    }

    calculations = []
    for calc_type, inputs in calc_types.items():
        calc = Calculation.create(calculation_type=calc_type, user_id=user.id, inputs=inputs)
        session.add(calc)
        calculations.append((calc_type, inputs, calc))

    session.commit()

    # Verify calculations
    for calc_type, inputs, calc in calculations:
        retrieved = session.query(Calculation).filter_by(id=calc.id).first()
        assert retrieved is not None
        assert retrieved.type == calc_type
        assert retrieved.inputs == inputs
        assert retrieved.user_id == user.id


def test_calculation_factory_invalid_type(session):
    """Test that the factory raises an error for unsupported types."""
    user = User(
        first_name="Bob",
        last_name="Brown",
        email="bob.brown@example.com",
        username="bobbrown",
        password="hashed_password"
    )
    session.add(user)
    session.commit()

    with pytest.raises(ValueError) as excinfo:
        Calculation.create(calculation_type="unsupported", user_id=user.id, inputs=[1, 2])
    assert "Unsupported calculation type: unsupported" in str(excinfo.value)


def test_addition_get_result(session):
    """Test the get_result method for Addition."""
    addition = Addition(user_id=uuid.uuid4(), inputs=[1, 2, 3, 4])
    result = addition.get_result()
    assert result == 10


def test_addition_get_result_invalid_inputs(session):
    """Test Addition with invalid inputs."""
    addition = Addition(user_id=uuid.uuid4(), inputs="not a list")
    with pytest.raises(ValueError) as excinfo:
        addition.get_result()
    assert "Inputs must be a list of numbers." in str(excinfo.value)


def test_subtraction_get_result(session):
    """Test the get_result method for Subtraction."""
    subtraction = Subtraction(user_id=uuid.uuid4(), inputs=[10, 3, 2])
    result = subtraction.get_result()
    assert result == 5


def test_subtraction_get_result_invalid_inputs(session):
    """Test Subtraction with invalid inputs."""
    subtraction = Subtraction(user_id=uuid.uuid4(), inputs=[10])
    with pytest.raises(ValueError) as excinfo:
        subtraction.get_result()
    assert "Inputs must be a list with at least two numbers." in str(excinfo.value)


def test_multiplication_get_result(session):
    """Test the get_result method for Multiplication."""
    multiplication = Multiplication(user_id=uuid.uuid4(), inputs=[2, 3, 4])
    result = multiplication.get_result()
    assert result == 24


def test_multiplication_get_result_invalid_inputs(session):
    """Test Multiplication with invalid inputs."""
    multiplication = Multiplication(user_id=uuid.uuid4(), inputs="not a list")
    with pytest.raises(ValueError) as excinfo:
        multiplication.get_result()
    assert "Inputs must be a list of numbers." in str(excinfo.value)


def test_division_get_result(session):
    """Test the get_result method for Division."""
    division = Division(user_id=uuid.uuid4(), inputs=[20, 2, 2])
    result = division.get_result()
    assert result == 5



def test_division_get_result_by_zero(session):
    """Test Division by zero."""
    division = Division(user_id=uuid.uuid4(), inputs=[10, 0])
    with pytest.raises(ValueError) as excinfo:
        division.get_result()
    assert "Cannot divide by zero." in str(excinfo.value)


def test_division_get_result_invalid_inputs(session):
    """Test Division with invalid inputs."""
    division = Division(user_id=uuid.uuid4(), inputs=[10])
    with pytest.raises(ValueError) as excinfo:
        division.get_result()
    assert "Inputs must be a list with at least two numbers." in str(excinfo.value)


def test_power_get_result(session):
    """Test the get_result method for Power."""
    power = Power(user_id=uuid.uuid4(), inputs=[2, 3])
    result = power.get_result()
    assert result == 8


def test_power_get_result_invalid_inputs(session):
    """Test Power with invalid inputs."""
    power = Power(user_id=uuid.uuid4(), inputs=[2])
    with pytest.raises(ValueError) as excinfo:
        power.get_result()
    assert "Inputs must be a list with exactly two numbers for power operation." in str(excinfo.value)


def test_modulus_get_result(session):
    """Test the get_result method for Modulus."""
    modulus = Modulus(user_id=uuid.uuid4(), inputs=[10, 3])
    result = modulus.get_result()
    assert result == 1


def test_modulus_get_result_by_zero(session):
    """Test Modulus by zero."""
    modulus = Modulus(user_id=uuid.uuid4(), inputs=[10, 0])
    with pytest.raises(ValueError) as excinfo:
        modulus.get_result()
    assert "Cannot perform modulus by zero!" in str(excinfo.value)


def test_modulus_get_result_invalid_inputs(session):
    """Test Modulus with invalid inputs."""
    modulus = Modulus(user_id=uuid.uuid4(), inputs=[10])
    with pytest.raises(ValueError) as excinfo:
        modulus.get_result()
    assert "Inputs must be a list with exactly two numbers for modulus operation." in str(excinfo.value)


def test_user_calculations_relationship(session):
    """Test the relationship between User and Calculations."""
    user = User(
        first_name="Charlie",
        last_name="Davis",
        email="charlie.davis@example.com",
        username="charliedavis",
        password="hashed_password"
    )
    session.add(user)
    session.commit()

    addition = Addition(user_id=user.id, inputs=[1, 2, 3])
    subtraction = Subtraction(user_id=user.id, inputs=[10, 5])
    session.add_all([addition, subtraction])
    session.commit()

    retrieved_user = session.query(User).filter_by(id=user.id).first()
    assert len(retrieved_user.calculations) == 2
    assert any(calc.type == 'addition' for calc in retrieved_user.calculations)
    assert any(calc.type == 'subtraction' for calc in retrieved_user.calculations)


def test_user_repr():
    """Test the __repr__ method of User."""
    user = User(first_name="Diana", last_name="Evans", email="diana.evans@example.com")
    repr_str = repr(user)
    assert "<User(name=Diana Evans, email=diana.evans@example.com)>" == repr_str
