
package src;


/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements selection sort.   
 *
 */

public class SelectionSorter extends AbstractSorter
{
	// Other private instance variables if you need ... 
	
	/**
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts  
	 */
	public SelectionSorter(Point[] pts) {
		super(pts);
		algorithm = "selection sort";
	}	
	
	/** 
	 * Apply selection sort on the array points[] of the parent class AbstractSorter.  
	 * 
	 */
	@Override 
	public void sort() {
		int size = points.length - 1;
		
		for (int i = 0; i < size; i++) {
			int minIndex = i;
			
			// Determines index with lowest value (x or y).
			for (int j = i + 1; j < size; j++) {
				if (pointComparator.compare(points[j], points[minIndex]) < 0) {
					minIndex = j;
				}
			}
			super.swap(i, minIndex); // Swaps min index with current index.
		}

	}	
}








