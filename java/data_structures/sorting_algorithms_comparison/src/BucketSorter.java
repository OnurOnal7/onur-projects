
package src;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the version of the bucket sort algorithm presented in the lecture.   
 *
 */

public class BucketSorter extends AbstractSorter
{
	
	// Other private instance variables if you need ... 
		
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *   
	 * @param pts   input array of integers
	 */
	public BucketSorter(Point[] pts){
		super(pts);
		algorithm = "bucket sort";
	}
		

	/**
	 * Carry out bucket sort on the array points[] of the AbstractSorter class.  
	 * 
	 */
	@Override
	public void sort() {
	    int max;
	    int min;

	    if (Point.xORy) {
	        max = Arrays.stream(points).mapToInt(Point::getX).max().orElse(0);
	        min = Arrays.stream(points).mapToInt(Point::getX).min().orElse(0);
	    } else {
	        max = Arrays.stream(points).mapToInt(Point::getY).max().orElse(0);
	        min = Arrays.stream(points).mapToInt(Point::getY).min().orElse(0);
	    }

	    int bucketCount = max - min + 1;

	    @SuppressWarnings("unchecked")
	    List<Point>[] buckets = new ArrayList[bucketCount];
	    for (int i = 0; i < bucketCount; i++) {
	        buckets[i] = new ArrayList<>();
	    }

	    for (Point point : points) {
	        int value = Point.xORy ? point.getX() : point.getY();
	        int bucketIndex = value - min;
	        buckets[bucketIndex].add(point);
	    }

	    for (int i = 0; i < bucketCount; i++) {
	        Collections.sort(buckets[i], pointComparator);
	    }

	    int currentIndex = 0;
	    for (int i = 0; i < bucketCount; i++) {
	        for (Point point : buckets[i]) {
	            points[currentIndex] = point;
	            currentIndex++;
	        }
	    }
	}

	
	
}
	
	

