
package src;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the cubesort algorithm.   
 *
 */

public class CubeSorter extends AbstractSorter
{

	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public CubeSorter(Point[] pts) {
		super(pts);
		algorithm = "cubesort";
	}


	/**
	 * Perform cubesort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override
	public void sort() {
	    int min, max;

	    // Find the minimum and maximum values based on x or y coordinates
	    if (Point.xORy) {
	        min = Arrays.stream(points).mapToInt(Point::getX).min().orElse(0);
	        max = Arrays.stream(points).mapToInt(Point::getX).max().orElse(0);
	    } else {
	        min = Arrays.stream(points).mapToInt(Point::getY).min().orElse(0);
	        max = Arrays.stream(points).mapToInt(Point::getY).max().orElse(0);
	    }

	    // Calculate the range of values
	    int range = max - min + 1;

	    // Create a 3D "cube" as a 3D array of Lists
	    @SuppressWarnings("unchecked")
		List<Point>[][] cube = new ArrayList[range][range];

	    // Initialize the cube with empty lists
	    for (int i = 0; i < range; i++) {
	        for (int j = 0; j < range; j++) {
	            cube[i][j] = new ArrayList<>();
	        }
	    }

	    // Place points in the cube based on their coordinates
	    for (Point point : points) {
	        int x, y;

	        if (Point.xORy) {
	            x = point.getX() - min;
	            y = point.getY() - min;
	        } else {
	            x = point.getY() - min;
	            y = point.getX() - min;
	        }

	        cube[x][y].add(point);
	    }

	    // Flatten the cube back into the original array
	    int index = 0;
	    for (int i = 0; i < range; i++) {
	        for (int j = 0; j < range; j++) {
	            for (Point point : cube[i][j]) {
	                points[index++] = point;
	            }
	        }
	    }
	}


}
