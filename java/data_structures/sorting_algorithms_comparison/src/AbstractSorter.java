
package src;

/**
 *  
 * @author Onur Onal
 *
 */

import java.util.Comparator;
import java.lang.IllegalArgumentException; 

/**
 * 
 * This abstract class is extended by SelectionSort, InsertionSort, MergeSort, and QuickSort.
 * It stores the input (later the sorted) sequence. 
 *
 */
public abstract class AbstractSorter {
	
	protected Point[] points;    // array of points operated on by a sorting algorithm. 
	                             // stores ordered points after a call to sort(). 
	
	protected String algorithm = null; // "selection sort", "insertion sort", "mergesort", or
	                                   // "quicksort". Initialized by a subclass constructor.
		 
	protected Comparator<Point> pointComparator = null;  
			
	/**
	 * This constructor accepts an array of points as input. Copy the points into the array points[]. 
	 * 
	 * @param  pts  input array of points 
	 * @throws IllegalArgumentException if pts == null or pts.length == 0.
	 */
	protected AbstractSorter(Point[] pts) throws IllegalArgumentException {
		if ((pts == null) || (pts.length == 0)) {
			throw new IllegalArgumentException("Array 'pts' cannot be null or empty");
		}
		
		points = new Point[pts.length];
		
		// Constructs the Point array.
		for (int i = 0; i < pts.length; i++) {
			points[i] = pts[i];
		}
	}


	/**
	 * Generates a comparator on the fly that compares by x-coordinate if order == 0, by y-coordinate
	 * if order == 1. Assign the 
     * comparator to the variable pointComparator. 
     *  
	 * 
	 * @param order  0   by x-coordinate 
	 * 				 1   by y-coordinate
	 * 			    
	 * 
	 * @throws IllegalArgumentException if order is less than 0 or greater than 1
	 *        
	 */
	public void setComparator(int order) throws IllegalArgumentException {
		// Inner class that implements Comparator<Point> interface.
		pointComparator = new Comparator<Point>() {
			@Override
			public int compare(Point a, Point b) {
				// Sets static boolean xORy based on value of order.
				if (order == 0) {
					Point.setXorY(true);
				}
				else if (order == 1) {
					Point.setXorY(false);
				}
				else {
					throw new IllegalArgumentException("Order must be 0 or 1");
				}
				return a.compareTo(b); // compareTo() inherently compares points by either x or y coordintes based on order.
 			}
		};
	}

	/**
	 * Use the created pointComparator to conduct sorting.  
	 * 
	 * Should be protected. Made public for testing. 
	 */
	protected abstract void sort(); 
	
	
	/**
	 * Obtain the point in the array points[] that has median index 
	 * 
	 * @return	median point 
	 */
	public Point getMedian(){
		return points[points.length/2]; 
	}
	
	
	/**
	 * Copys the array points[] onto the array pts[]. 
	 * 
	 * @param pts
	 */
	public void getPoints(Point[] pts){
		// Calls the Point class' "Clone" constructor.
		for (int i = 0; i < points.length; i++) {
			pts[i] = new Point(points[i]);
		}
	}

	/**
	 * Swaps the two elements indexed at i and j respectively in the array points[]. 
	 * 
	 * @param i
	 * @param j
	 */
	protected void swap(int i, int j) {   
		// Prevents code duplication in SelectionSort, QuickSort.
		Point temp = points[i];
		points[i] = points[j];   
		points[j] = temp;
	}	
}






