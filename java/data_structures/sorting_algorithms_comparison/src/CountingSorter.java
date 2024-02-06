
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the version of the counting sort algorithm presented in the lecture.   
 *
 */

public class CountingSorter extends AbstractSorter
{
	
	// Other private instance variables if you need ... 
		
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *   
	 * @param pts   input array of integers
	 */
	public CountingSorter(Point[] pts){
		super(pts);
		algorithm = "counting sort";
	}
		

	/**
	 * Carry out counting sort on the array points[] of the AbstractSorter class.  
	 * 
	 */
	@Override
	public void sort() {
		// Find the maximum and minimum values based on the custom comparator
	    Point maxPoint = points[0];
	    Point minPoint = points[0];

	    for (Point point : points) {
	        if (pointComparator.compare(point, maxPoint) > 0) {
	            maxPoint = point;
	        }

	        if (pointComparator.compare(point, minPoint) < 0) {
	            minPoint = point;
	        }
	    }

	    int range = pointComparator.compare(maxPoint, minPoint) + 1;

	    // Create a count array to store the frequency of each element
	    int[] countArray = new int[range];

	    // Count the occurrences of each element in the input array
	    for (Point point : points) {
	        int index = pointComparator.compare(point, minPoint);
	        countArray[index]++;
	    }

	    // Update the count array to store the actual positions of elements
	    for (int i = 1; i < range; i++) {
	        countArray[i] += countArray[i - 1];
	    }

	    // Create an output array to store the sorted elements
	    Point[] output = new Point[points.length];

	    // Build the output array based on the count array
	    for (int i = points.length - 1; i >= 0; i--) {
	        int index = pointComparator.compare(points[i], minPoint);
	        output[countArray[index] - 1] = points[i];
	        countArray[index]--;
	    }

	    // Copy the sorted elements back to the original array
	    System.arraycopy(output, 0, points, 0, points.length);
	}

	
	
}
	
	