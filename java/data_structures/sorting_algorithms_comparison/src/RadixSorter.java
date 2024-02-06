
package src;

import java.util.Arrays;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the radix sort algorithm.   
 *
 */

public class RadixSorter extends AbstractSorter
{

	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public RadixSorter(Point[] pts) {
		super(pts);
		algorithm = "radix sort";
	}


	/**
	 * Perform radix sort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override
	public void sort() {
	    int max;
	    int min; // To store the minimum value
	    
	    // Find the maximum and minimum values based on x or y coordinates
	    if (Point.xORy) {
	        max = Arrays.stream(points).mapToInt(Point::getX).max().orElse(0);
	        min = Arrays.stream(points).mapToInt(Point::getX).min().orElse(0);
	    } else {
	        max = Arrays.stream(points).mapToInt(Point::getY).max().orElse(0);
	        min = Arrays.stream(points).mapToInt(Point::getY).min().orElse(0);
	    }

	    // Adjust the minimum value to make it non-negative
	    int adjustment = min < 0 ? -min : 0;

	    // Make sure that the maximum value of exp is a power of 10
	    int maxExp = 1;
	    while ((max + adjustment) / maxExp > 0) {
	        maxExp *= 10;
	    }

	    for (int exp = 1; exp <= maxExp; exp *= 10) {
	        countingSort(points, exp, Point.xORy, adjustment);
	    }
	}

	private static void countingSort(Point[] arr, int exp, boolean xORy, int adjustment) {
	    int size = arr.length;
	    Point[] output = new Point[size];
	    
	    // Determine the range of values (0-9 for digits)
	    int range = 10;
	    int[] counts = new int[range];
	    
	    // Initialize the count array
	    Arrays.fill(counts, 0);

	    // Count occurrences of digits at the current place value
	    for (int i = 0; i < size; i++) {
	        int value = xORy ? arr[i].getX() : arr[i].getY();
	        int digit = ((value + adjustment) / exp) % 10;

	        // Ensure that the digit is within the valid range (0 to 9)
	        if (digit < 0) {
	            throw new IllegalArgumentException("Negative digit encountered: " + digit);
	        }

	        counts[digit]++;
	    }

	    // Modify counts to contain actual positions of the digits in the output
	    for (int i = 1; i < range; i++) {
	        counts[i] += counts[i - 1];
	    }

	    // Build the output array by placing elements in their sorted positions
	    for (int i = size - 1; i >= 0; i--) {
	        int value = xORy ? arr[i].getX() : arr[i].getY();
	        int digit = ((value + adjustment) / exp) % 10;
	        int index = counts[digit] - 1;
	        output[index] = arr[i];
	        counts[digit]--;
	    }

	    // Copy the output array to the original array
	    System.arraycopy(output, 0, arr, 0, size);
	}

}





