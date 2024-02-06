import random
import matplotlib.pyplot as plt
from PIL import Image as im

# Initialize a 2D array with initial data
graphing_data = [
    [26, 72, 33],
    [45, 35, 69],
    [71, 28, 62]
]


def create_graph(data):
    # Check if the specified data index is within the range of the 2D array
    if data < 0 or data >= len(graphing_data):
        print("Invalid data index")
        return

    # Get the row corresponding to the given data index
    row = graphing_data[data]

    # Determine the initial max and min points locally
    max_pressure = max(row)
    min_pressure = min(row)
    max_idx = row.index(max_pressure)
    min_idx = row.index(min_pressure)

    # Create a figure for the graph
    fig = plt.figure()

    # Configure the plot
    ax = fig.add_subplot(111)
    ax.set_xlabel('Time (seconds)')

    if data == 0:
        title = "Hydraulic Pressure vs. Time"
        y_label = "Pressure (psi)"
    elif data == 1:
        title = "Airlock Oxygen Concentration vs. Time"
        y_label = "Oxygen (ppm)"
    else:
        title = "Glovebox Oxygen Concentration vs. Time"
        y_label = "Oxygen (ppm)"

    ax.set_ylabel(y_label)
    ax.set_title(title)

    # Lists to keep track of maximum and minimum markers
    max_markers = [ax.plot(max_idx, max_pressure, 'ro')[0]]
    min_markers = [ax.plot(min_idx, min_pressure, 'bo')[0]]

    # Simulate data updates and plot
    while True:
        # Simulate data update by appending a random integer value between 10 and 100
        random_pressure = random.randint(20, 80)
        row.append(random_pressure)

        # Update the plot data
        ax.plot(range(len(row)), row, color='black')

        # Find and mark the max and min points in the newly added data
        if random_pressure > max_pressure:
            max_pressure = random_pressure
            max_idx = len(row) - 1
            # Remove the previous max marker and add the new one
            for marker in max_markers:
                marker.remove()
            max_markers = [ax.plot(max_idx, max_pressure, 'ro')[0]]

        if random_pressure < min_pressure:
            min_pressure = random_pressure
            min_idx = len(row) - 1
            # Remove the previous min marker and add the new one
            for marker in min_markers:
                marker.remove()
            min_markers = [ax.plot(min_idx, min_pressure, 'bo')[0]]

        # Adjust the x-axis limits to show the entire data history
        ax.relim()
        ax.autoscale_view()

        # Pause for 1 second
        plt.pause(1)

        # Save the plot as a PNG
        fig.savefig('graph.png', dpi=250)

        # Convert the PNG to BMP (overwriting the previous BMP image)
        im.open("graph.png").save("graph.bmp")


# Example usage
data_index = 2  # Replace this with the desired data index (0, 1, or 2)
create_graph(data_index)



