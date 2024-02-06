
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the mergesort algorithm.   
 *
 */

public class MergeSorter extends AbstractSorter
{
	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public MergeSorter(Point[] pts) {
		super(pts);
		algorithm = "mergesort";
	}


	/**
	 * Perform mergesort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override 
	public void sort() {
		if (points.length <= 1) {
			return;
		}
		
	    mergeSortRec(points);
	}

	
	/**
	 * This is a recursive method that carries out mergesort on an array pts[] of points. One 
	 * way is to make copies of the two halves of pts[], recursively call mergeSort on them, 
	 * and merge the two sorted subarrays into pts[].   
	 * 
	 * @param pts	point array 
	 */
	private void mergeSortRec(Point[] pts) {
		int size = pts.length;
		
		if (size <= 1) {
    		return;
    	}
		
		// Parts point array into two halves.
		int middle = size / 2;
		Point[] left = new Point[middle];
		Point[] right = new Point[size - middle];
		
		// Copies appropriate partitions of pts array into left and right arrays. 
		System.arraycopy(pts, 0, left, 0, left.length);
    	System.arraycopy(pts, middle, right, 0, right.length);
    	
    	// Recursively partitions halves into smaller halves. 
    	mergeSortRec(left);
    	mergeSortRec(right);

    	merge(left, right, pts); // merges two halves, sorting them into pts.
	}

	
	// Method to merge left and right partitions into source array.
	private void merge(Point[] left, Point[] right, Point[] pts) {
		int p = left.length, q = right.length;
		int i = 0, j = 0, k = 0;
		
		// Merges two halves into single sorted array.
		while ((i < p) && (j < q)) {
			if (pointComparator.compare(left[i], right[j]) <= 0) {
				pts[k++] = left[i++];
			}
			else {
				pts[k++] = right[j++];
			}
		}
		
		while (i < p) {
			pts[k++] = left[i++];
		}
		
		while (j < q) {
			pts[k++] = right[j++];
		}
	}
	
}



