
package src;


/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements insertion sort.   
 *
 */

public class InsertionSorter extends AbstractSorter 
{
	// Other private instance variables if you need ... 
	
	/**
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 * 
	 * @param pts  
	 */
	public InsertionSorter(Point[] pts) {
		super(pts);
		algorithm = "insertion sort";
	}	

	/** 
	 * Perform insertion sort on the array points[] of the parent class AbstractSorter.  
	 */
	@Override 
	public void sort(){
		int size = points.length;
		Point tempPoint;
		
		for (int i = 1; i < size; i++) {
			tempPoint = points[i];
			int j = i - 1;
			
			// Compares point with points preceding itself to find its position.
			while ((j > -1) && (pointComparator.compare(points[j], tempPoint)) > 0) {
				points[j + 1] = points[j]; // Slides points to the right to make way for temp point.
				j--;
			}
			points[j + 1] = tempPoint; // Places the point in approprite positioning.
		}
	}		
}



