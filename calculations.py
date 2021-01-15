"""Model our increase in data by doing a linear regression on carbon dioxide emissions and temperature.
This assumes that our data starts and ends on the same years, which we put to be 1975 and 2019
"""
import csv
import datetime
from typing import List, Tuple
import random


def current_future(c_data: list, t_data: list, years: int) -> List[Tuple[datetime.date, float]]:
    """Extrapolates the future based on previous carbon data,
    temperature data, and a year given by the slider

    Preconditions:
        - c_data.length == t_data.length
        - years >= 0
    """

    c_reg = linear_regression(c_data)
    t_reg = linear_regression(t_data)
    final_coefficient = coefficient(c_reg, t_reg)
    return append_data(c_data, t_data, years, final_coefficient)


def possible_future(c_data: list, t_data: list, years: int, input: float) -> List[Tuple[datetime.date, float]]:
    """Extrapolates the future based on previous carbon data, temperature data,
    a year given by the current_future(c_data, t_data, 2) slider and a coefficient of change

    Preconditions:
        - c_data.length == t_data.length
        - years >= 0
    """
    t_reg = linear_regression(t_data)
    final_coefficient = (input, t_reg[0])
    final_coefficient = coefficient((0, input), t_reg)
    return append_data(c_data, t_data, years, final_coefficient)


def read_carbon_data(filepath: str) -> List[Tuple[datetime.date, float]]:
    """Returns a list of tuples from the data mapped from a CSV file for carbon dioxide data.

    Returns a list of tuples corresponding to the format of: (date, CO2)

    CO2 expressed as a mole fraction in dry air, micromol/mol, abbreviated as ppm

    Preconditions:
        - filepath refers to a csv file in the format of co2_data.csv
          (i.e., could be that file or a different file in the same format)
    """
    with open(filepath) as file:
        reader = csv.reader(file)

        # Skip header row
        next(reader)

        data_so_far = []

        for row in reader:
            data_so_far.append((datetime.date(int(row[0]), int(row[1]), 1), float(row[3])))

    return data_so_far


def read_temperature_data(filepath: str) -> List[Tuple[datetime.date, float]]:
    """Returns a list of tuples from the data mapped from a CSV file for monthly temperature data.

    Returns a list of tuples corresponding to the format of: (date, temperature)

    Temperature is expressed in degrees Celsius.

    Preconditions:
        - filepath refers to a csv file in the format of temperature_data.csv
          (i.e., could be that file or a different file in the same format)
    """
    with open(filepath) as file:
        reader = csv.reader(file)

        # Skip header row
        next(reader)

        data_so_far = []

        for row in reader:
            for month in range(1, 13):
                data_so_far.append((datetime.date(int(row[0]), month, 1), float(row[month])))

    return data_so_far


def convert_points(points: list) -> tuple:
    """Return a tuple of two lists, containing the x- and y-coordinates of the given points.

    Preconditions:
        - points is a list of tuples, where each tuple is a list of floats.

    >>> result = convert_points([(0.0, 1.1), (2.2, 3.3), (4.4, 5.5)])
    >>> result[0]  # The x-coordinates
    [0.0, 2.2, 4.4]
    >>> result[1]  # The y-coordinates
    [1.1, 3.3, 5.5]
    """
    x_coords = [points[i][0] for i in range(0, len(points))]
    y_coords = [points[i][1] for i in range(0, len(points))]
    return (x_coords, y_coords)


def averaged(nums: list) -> float:
    """ Gives an average of the values in a list

    Preconditions: len(nums) > 0
    """
    return sum(nums) / len(nums)


def linear_regression(data: list) -> tuple:
    """Perform a linear regression on the given points, returns an
    averaged value over the course of the year based on individual months. From the

    points refers to a list of pairs of floats [(x_1, y_1), (x_2, y_2), ...]

    This function returns a pair of floats (a, b) such that the line
    y = a + bx is the approximation of this data.

    Preconditions:
        - len(points) > 0
        - each element of points is a tuple of two floats
    """
    lin_reg_months = []
    startyear = 1975
    endyear = 2019

    # Calculates a linear regression for each individual month.
    for month in range(0, 12):
        points = []
        for i in range(startyear, endyear):
            points.append((i - startyear, data[(i - startyear) * 12 + month][1]))
        converted = convert_points(points)
        x_coords = converted[0]
        y_coords = converted[1]
        x_avg = averaged(x_coords)
        y_avg = averaged(y_coords)
        topb = sum((points[i][0] - x_avg) * (points[i][1] - y_avg) for i in range(0, len(points)))
        bottomb = sum((points[p][0] - x_avg) ** 2 for p in range(0, len(points)))
        b = topb / bottomb
        a = y_avg - b * x_avg
        lin_reg_months.append((a, b))

    # Gets the average of each linear regression of the month
    averaged_a = sum(month[0] for month in lin_reg_months) / len(lin_reg_months)
    averaged_b = sum(month[1] for month in lin_reg_months) / len(lin_reg_months)
    return (averaged_a, averaged_b)


def extrapolate_data(data: list, b: float, years: int) -> List[Tuple[datetime.date, float]]:
    """Returns extrapolated data given previous data, as well as a constant growth value
    for a set amount of years.

    Preconditions:
        - len(data) > 0
        - years >= 0
    """

    return_values = []
    months = years * 12
    date = data[len(data) - 1][0]
    add = b + random.random() * b * 0.01
    for i in range(1, 13):
        return_values.append((date + datetime.timedelta(weeks=i * 4.33), data[len(data) - (13 - i)][1] + add))

    for i in range(1, months - 11):
        return_values.append((return_values[11][0] + datetime.timedelta(weeks=i*4.33), return_values[i - 1][1] + add))

    return return_values


def coefficient(carbon_regression: Tuple, temperature_regression: Tuple) -> Tuple[float, float]:
    """Returns a coefficient and constant to convert carbon to temperature in the form
    y = ax + b where the returned value is (a, b)"""

    return (carbon_regression[1], temperature_regression[0])


def append_data(c_data: list, t_data: list, years: int, coeff: Tuple) -> List[Tuple[datetime.date, float]]:
    """Mutates the initial data list by appending the future_carbon_data onto it"""
    carbon_regression = linear_regression(c_data)
    future_temperature = t_data.copy()
    future_data = extrapolate_data(c_data, carbon_regression[1], years)
    curr = len(future_temperature)
    for i in range(0, len(future_data)):
        temperature = carbon_to_temperature(future_data[i][1], coeff, i)
        future_temperature.append((future_data[i][0],
                                   t_data[i][1] + temperature))
    return future_temperature


def carbon_to_temperature(carbon: float, coeff: Tuple, year) -> float:
    """Converts the CO2 levels to a change in temperature based on our calculation of the y = bx + a equation
    and a calculated constant based on the average approximated change in temperature since 1975 of Ontario"""
    print(str(coeff[0]) + " " + str(coeff[1]))
    return (carbon + (coeff[0] * year / 12)) * 0.018 - coeff[1] + 1.30

