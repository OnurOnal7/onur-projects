
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the shell sort algorithm.   
 *
 */

public class ShellSorter extends AbstractSorter
{

	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public ShellSorter(Point[] pts) {
		super(pts);
		algorithm = "shell sort";
	}


	/**
	 * Perform shell sort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override
	public void sort() {
		int n = points.length;
        
        // Start with a large gap and reduce it until gap becomes 1
        for (int gap = n / 2; gap > 0; gap /= 2) {
            // Perform insertion sort for elements at each gap
            for (int i = gap; i < n; i++) {
                Point key = points[i];
                int j = i;
                
                // Move elements that are greater than key to the right
                while (j >= gap && pointComparator.compare(points[j - gap], key) > 0) {
                    points[j] = points[j - gap];
                    j -= gap;
                }
                
                points[j] = key;
            }
        }
	}

	

}





