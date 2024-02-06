
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class executes four sorting algorithms: selection sort, insertion sort, mergesort, and
 * quicksort, over randomly generated integers as well integers from a file input. It compares the 
 * execution times of these algorithms on the same input. 
 *
 */

import java.io.FileNotFoundException;
import java.util.InputMismatchException;
import java.util.Random;
import java.util.Scanner; 


public class CompareSorters 
{
	/**
	 * Repeatedly take integer sequences either randomly generated or read from files. 
	 * Use them as coordinates to construct points.  Scan these points with respect to their 
	 * median coordinate point four times, each time using a different sorting algorithm.  
	 * 
	 * @param args
	 **/
	public static void main(String[] args) throws FileNotFoundException, InputMismatchException {		
		PointScanner[] scanners = new PointScanner[13]; 
		Algorithm[] algos = Algorithm.values(); // Creating algorithm array to iterate through algorithms while iterating through scanners.

		Random rand = new Random();
		Scanner scnr = new Scanner(System.in);
		
		System.out.println("Performances of Four Sorting Algorithms in Point Scanning");
		System.out.println();
		System.out.println("keys: 1 (random integers) 2 (file input) 3 (exit)");
		
		int trial = 1; // The number of trials the user has done.
	
		try {
			while (true) {
				System.out.println("Trial " + trial + ": ");
				int key = scnr.nextInt();
				
				if (key == 1) {
					System.out.println("Enter number of random points: ");
					int numPoints = scnr.nextInt();
					
					Point[] points = generateRandomPoints(numPoints, rand); // Constructs points array with random numbers
					
					System.out.println();
					System.out.println("algorithm   size  time (ns)");
					System.out.println("----------------------------------");
					
					// Scans and prints stats of sorting results for each algorithm, using a new PointScanner each time. 
					for (int i = 0; i < scanners.length; i++) {
						scanners[i] = new PointScanner(points, algos[i]);
						scanners[i].scan();
						System.out.println(scanners[i].stats());
					}
				}
				else if (key == 2) {
					try {
						System.out.println("File name: ");
						String fileName = scnr.next();
						
						System.out.println();
						System.out.println("algorithm   size  time (ns)");
						System.out.println("----------------------------------");
						
						// Scans and prints stats of sorting results for each algorithm, using a new PointScanner each time. 
						for (int i = 0; i < scanners.length; i++) {
							scanners[i] = new PointScanner(fileName, algos[i]);
							scanners[i].scan();
							System.out.println(scanners[i].stats());

						}		
					}
					catch (FileNotFoundException e) {
		                System.out.println("File not found."); // Prints error to allow user to continue trials.
					}
				}
				else if (key == 3) {
					break; // Exit
				}
				else {
					throw new InputMismatchException("Invalid key."); // Throw error if key is not 1, 2, or 3.
				}
				
				System.out.println("----------------------------------");
				System.out.println();
				trial++;
			}	
		}
		finally {
			scnr.close(); // Closing scanner in outer try-catch to avoid warning for scnr.
		}		
	}
	
	
	/**
	 * This method generates a given number of random points.
	 * The coordinates of these points are pseudo-random numbers within the range 
	 * [-50,50] � [-50,50]. Please refer to Section 3 on how such points can be generated.
	 * 
	 * Ought to be private. Made public for testing. 
	 * 
	 * @param numPts  	number of points
	 * @param rand      Random object to allow seeding of the random number generator
	 * @throws IllegalArgumentException if numPts < 1
	 */
	private static Point[] generateRandomPoints(int numPts, Random rand) throws IllegalArgumentException { 
		if (numPts < 1) {
			throw new IllegalArgumentException("Invalid number of points");
		}
		
		Point[] randPoints = new Point[numPts]; 
		
		for (int i = 0; i < randPoints.length; i++) {
			// Constructs points in the point array with consecutive random numbers as x and y coordinates respectively.
			int x = rand.nextInt(101) - 50;
			int y = rand.nextInt(101) - 50;
			randPoints[i] = new Point(x, y);
		}
		
		return randPoints;
	}
	
}




