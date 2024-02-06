
package src;

import java.util.Arrays;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements timsort.   
 *
 */

public class TimSorter extends AbstractSorter 
{
	// Other private instance variables if you need ... 
	
	/**
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 * 
	 * @param pts  
	 */
	public TimSorter(Point[] pts) {
		super(pts);
		algorithm = "timsort";
	}	

	/** 
	 * Perform timsort on the array points[] of the parent class AbstractSorter.  
	 */
	@Override 
	public void sort(){
        Arrays.sort(points, pointComparator);
		
	}		
}



