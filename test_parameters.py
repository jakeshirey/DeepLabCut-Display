import pytest
import numpy as np
import pandas as pd
import gait_parameters as gp

from PyQt5.QtWidgets import QApplication

# Import the angle() and distance() functions here
@pytest.fixture
def app(request):
    application = QApplication([])
    yield application
    application.quit()

@pytest.fixture
def widget(request):
    widget = gp.ParameterInputDialog([], pd.read_excel('test_data/3613data.xlsx'))
    widget.confirmed_landmarks = {'Nostril': 'nostril', 'Poll': 'poll', 'Withers': 'withers', 'Shoulder': 'shoulder', 'Elbow': 'elbow', 
                                  'Mid Back': 'midback', 'Croup': 'croup', 'Hip': 'hip', 'Stifle': 'stifle', 'Dock': 'NOT AVAILABLE', 
                                  'Left Front Hoof': 'leftFhoof', 'Left Hind Hoof': 'leftHhoof', 'Left Hock': 'lefthock', 
                                  'Left Front Fetlock': 'rightFfetlock', 'Left Hind Fetlock': 'rightHfetlock', 'Left Knee': 'leftknee', 
                                  'Right Front Hoof': 'rightFhoof', 'Right Hind Hoof': 'rightHhoof', 'Right Hock': 'righthock', 
                                  'Right Front Fetlock': 'rightFfetlock', 'Right Hind Fetlock': 'rightHfetlock', 'Right Knee': 'rightknee'}
    widget.queried_gait_parameters = ['Right Shank', 'Left Shank', 'Head', 'Hind Limb Length', 'Hind Leg Length', 'Fore Limb Length', 
                                      'Fore Leg Length', 'Neck Length', 'Fore Limb Angle', 'Hind Limb Angle', 'Fore Fetlock Angle', 'Hind Fetlock Angle']
    widget.summ_stats = ['Minimum', 'Maximum', 'Average', 'Standard Deviation']

    #clean data by combining labels and reindexing
    bodyparts_labels = widget.data.loc[0]
    coords_labels = widget.data.loc[1]
    labels = [i + "_" + j for i, j in zip(bodyparts_labels, coords_labels)]
    widget.data.columns = labels
    widget.data = widget.data.iloc[2: , : ]
    widget.data.index = range(len(widget.data.index))
    widget.data = widget.data.drop(columns=["bodyparts_coords"])
    yield widget

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

def test_vectorized_angle():
    df = pd.DataFrame({'vertex_x': [0, 1, 2],
                    'vertex_y': [0, 1, 2],
                    'point1_x': [1, 2, 3],
                    'point1_y': [0, 1, 2],
                    'point2_x': [0, 1, 2],
                    'point2_y': [1, 2, 3],
                    'angle': [90.0, 90.0, 90.0]})
    # Apply the angle function using vectorized operations
    df['computed_angle'] = np.vectorize(gp.angle, signature='(n),(n),(n)->()')(df[['vertex_x', 'vertex_y']].values,
                                                                             df[['point1_x', 'point1_y']].values,
                                                                             df[['point2_x', 'point2_y']].values)
    assert np.allclose(df['computed_angle'], df['angle'])

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


def test_shank_calculation(app, widget):
    calc_frame = pd.DataFrame(columns=widget.queried_gait_parameters, index=widget.data.index)
    calc_frame['Right Shank'] = widget.vectorized_distance(column1="Right Hock", column2= "Right Hind Fetlock")
    QApplication.processEvents()
    correct_right_shank = pd.read_excel('test_data/3613correct_right_shank.xlsx')
    assert np.allclose(calc_frame["Right Shank"], correct_right_shank["Right Shank"])


# Run the tests
pytest.main()
