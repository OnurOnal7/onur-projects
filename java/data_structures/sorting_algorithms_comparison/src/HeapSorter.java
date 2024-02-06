
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the heapsort algorithm.   
 *
 */

public class HeapSorter extends AbstractSorter
{

	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public HeapSorter(Point[] pts) {
		super(pts);
		algorithm = "heapsort";
	}


	/**
	 * Perform heapsort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override
	public void sort() {
	    buildMaxHeap();
	    
	    for (int i = points.length - 1; i >= 0; i--) {
	        super.swap(0, i);
	        maxHeapify(0, i);
	    }
	}

	private void buildMaxHeap() {
	    int size = points.length;
	    for (int i = size / 2 - 1; i >= 0; i--) {
	        maxHeapify(i, size);
	    }
	}

	private void maxHeapify(int index, int size) {
	    int leftChildIndex = 2 * index + 1;
	    int rightChildIndex = 2 * index + 2;
	    int largestIndex = index;

	    if (leftChildIndex < size && pointComparator.compare(points[leftChildIndex], points[largestIndex]) > 0) {
	        largestIndex = leftChildIndex;
	    }

	    if (rightChildIndex < size && pointComparator.compare(points[rightChildIndex], points[largestIndex]) > 0) {
	        largestIndex = rightChildIndex;
	    }

	    if (largestIndex != index) {
	        super.swap(index, largestIndex);
	        maxHeapify(largestIndex, size);
	    }
	}

}



