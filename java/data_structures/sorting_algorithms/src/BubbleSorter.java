
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the bubble sort algorithm.   
 *
 */

public class BubbleSorter extends AbstractSorter
{

	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public BubbleSorter(Point[] pts) {
		super(pts);
		algorithm = "bubble sort";
	}


	/**
	 * Perform bubble sort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override
	public void sort() {
		int size = points.length;
		boolean swapped;

		do {
            swapped = false;
            for (int i = 1; i < size; i++) {
                // If this pair is out of order
                if (pointComparator.compare(points[i - 1], points[i]) > 0) {
                    // Swap them and remember something changed
                    swap(i - 1, i);
                    swapped = true;
                }
            }
        } while (swapped);
    }
	

}





