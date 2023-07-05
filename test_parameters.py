import pytest
import numpy as np
import pandas as pd
import gait_parameters as gp

# Import the angle() and distance() functions here

def test_angle():
    # Test case 1: Points forming a right angle
    angle_1 = gp.angle([0, 0], [1, 0], [0, 1])  # Expected angle: 90 degrees
    assert np.isclose(angle_1, 90.0)

    # Test case 2: Points forming an acute angle
    angle_2 = gp.angle([0, 0], [1, 0], [1, 1])  # Expected angle: 45 degrees
    assert np.isclose(angle_2, 45.0)

    # Test case 3: Points forming an obtuse angle
    angle_3 = gp.angle([0, 0], [1, 0], [-1, 1])  # Expected angle: 135 degrees
    assert np.isclose(angle_3, 135.0)

def test_distance():
    # Test case 1: Points with same x-coordinate
    distance_1 = gp.distance([0, 0], [0, 5])  # Expected distance: 5.0
    assert np.isclose(distance_1, 5.0)

    # Test case 2: Points with same y-coordinate
    distance_2 = gp.distance([0, 0], [3, 0])  # Expected distance: 3.0
    assert np.isclose(distance_2, 3.0)

    # Test case 3: General case
    distance_3 = gp.distance([0, 0], [3, 4])  # Expected distance: 5.0
    assert np.isclose(distance_3, 5.0)

def test_vectorized_distance():
    df = pd.DataFrame({'landmark1_x': [1, 2, 3],
                   'landmark1_y': [4, 5, 6],
                   'landmark2_x': [7, 8, 9],
                   'landmark2_y': [10, 11, 12],
                   'distance': [8.485281, 8.485281, 8.485281]})
    # Apply the distance function using vectorized operations
    df['computed_distance'] = np.vectorize(gp.distance, signature='(n),(n)->()')(df[['landmark1_x', 'landmark1_y']].values,
                                                                              df[['landmark2_x', 'landmark2_y']].values)

    # Check if the computed distances match the expected distances
    assert np.allclose(df['computed_distance'], df['distance'])
# Run the tests
pytest.main()
