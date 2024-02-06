
package src;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.InputMismatchException;
import java.util.Scanner;

/**
 * 
 * @author Onur Onal
 *
 */

/**
 * 
 * This class sorts all the points in an array of 2D points to determine a reference point whose x and y 
 * coordinates are respectively the medians of the x and y coordinates of the original points. 
 * 
 * It records the employed sorting algorithm as well as the sorting time for comparison. 
 *
 */
public class PointScanner  
{
	private Point[] points; 
	
	private Point medianCoordinatePoint;  // point whose x and y coordinates are respectively the medians of 
	                                      // the x coordinates and y coordinates of those points in the array points[].
	private Algorithm sortingAlgorithm;   
	
	private AbstractSorter aSorter;  // AbstractSorter as private variable to use algorithm variable in stats() method.
		
	protected long scanTime; 	       // execution time in nanoseconds. 
	
	/**
	 * This constructor accepts an array of points and one of the four sorting algorithms as input. Copy 
	 * the points into the array points[].
	 * 
	 * @param  pts  input array of points 
	 * @throws IllegalArgumentException if pts == null or pts.length == 0.
	 */
	public PointScanner(Point[] pts, Algorithm algo) throws IllegalArgumentException {
		if ((pts == null) || (pts.length == 0)) {
			throw new IllegalArgumentException("Array 'pts' cannot be null or empty");
		}
		
		points = new Point[pts.length];
		
		// Constructs the Point array.
		for (int i = 0; i < pts.length; i++) {
			points[i] = pts[i];
		}
		
		sortingAlgorithm = algo;
	}

	
	/**
	 * This constructor reads points from a file. 
	 * 
	 * @param  inputFileName
	 * @throws FileNotFoundException 
	 * @throws InputMismatchException   if the input file contains an odd number of integers
	 */
	protected PointScanner(String inputFileName, Algorithm algo) throws FileNotFoundException, InputMismatchException {
		File file = new File(inputFileName);
		
		ArrayList<Integer> coords = new ArrayList<Integer>(); // Arraylist to arrange all numbers from file to be used as x or y coords.
			
		try (Scanner scnr = new Scanner(file)) {
			while (scnr.hasNextLine()) {
				String line = scnr.nextLine();
				Scanner lineScnr = new Scanner(line);
				
				while (lineScnr.hasNextInt()) {
					int coord = lineScnr.nextInt(); 
					coords.add(coord); // Adding numbers from file to arraylist.
				}
				lineScnr.close();
			}
			scnr.close();
		}
		catch (FileNotFoundException e) {
			throw new FileNotFoundException("Input file " + inputFileName + " not found.");
		}
		
		// Checks for odd number of integers in input file.
		if (coords.size() % 2 == 1) {
			throw new InputMismatchException("Input file contains an odd number of integers");
		}
		
		ArrayList<Point> pointsList = new ArrayList<Point>(); // Arraylist to succesively create Point objects with coordinates obtained from "coords."
		
		// Creates points from coords by iterating += 2, each time using two values from "coords" to obtain x and y.
		for (int i = 0; i < coords.size(); i += 2) {
			Point point = new Point(coords.get(i), coords.get(i + 1));
			pointsList.add(point);
		}
		
		points = new Point[pointsList.size()]; // Constructs points array with size "pointsList."
		
		// Maps arraylist of points to array of points.
		for (int i = 0; i < pointsList.size(); i++) {
		    points[i] = pointsList.get(i);
		}

		sortingAlgorithm = algo;
	}
	

	
	/**
	 * Carry out two rounds of sorting using the algorithm designated by sortingAlgorithm as follows:  
	 *    
	 *     a) Sort points[] by the x-coordinate to get the median x-coordinate. 
	 *     b) Sort points[] again by the y-coordinate to get the median y-coordinate.
	 *     c) Construct medianCoordinatePoint using the obtained median x- and y-coordinates.     
	 *  
	 * Based on the value of sortingAlgorithm, create an object of SelectionSorter, InsertionSorter, MergeSorter,
	 * or QuickSorter to carry out sorting.       
	 * @param algo
	 * @return
	 */
	public void scan() {		
		// Sets dynamic type of "AbstractSorter" object based on Algorithm enum.
		switch (sortingAlgorithm) {
			case SelectionSort:
				aSorter = new SelectionSorter(points);
				break;
			case InsertionSort:
				aSorter = new InsertionSorter(points);
				break;
			case MergeSort:
				aSorter = new MergeSorter(points);
				break;
			case QuickSort:
				aSorter = new QuickSorter(points);
				break;
			case BubbleSort:
				aSorter = new BubbleSorter(points);
				break;
			case RadixSort:
				aSorter = new RadixSorter(points);
				break;
			case TimSort:
				aSorter = new TimSorter(points);
				break;
			case HeapSort:
				aSorter = new HeapSorter(points);
				break;
			case TreeSort:
				aSorter = new TreeSorter(points);
				break;
			case ShellSort:
				aSorter = new ShellSorter(points);
				break;
			case BucketSort:
				aSorter = new BucketSorter(points);
				break;
			case CountingSort:
				aSorter = new CountingSorter(points);
				break;
			case CubeSort:
				aSorter = new CubeSorter(points);
				break;
			default:
				aSorter = null;
                break;
		}
				
		if (aSorter != null) {
			// Local variables for median and time collection.
			long startTime, endTime;
		    long totalTimeX, totalTimeY;
		    int medianX, medianY;
		    
			aSorter.setComparator(0); // Sets comparator to compare x values.
			startTime = System.nanoTime(); // Starts time.
			aSorter.sort(); // Calls sort of current child class of AbstractSorter.
			endTime = System.nanoTime(); // Stops time.
			totalTimeX = endTime - startTime; // Finds total time for sorting of points based on x.
			medianX = aSorter.getMedian().getX(); // Gets the x coordinate of the median point sorted by x.
			
			aSorter.setComparator(1); // Sets comparator to compare y values.
			startTime = System.nanoTime(); // Starts time.
			aSorter.sort(); // Calls sort of current child class of AbstractSorter.
			endTime = System.nanoTime(); // Stops time.
			totalTimeY = endTime - startTime; // Finds total time for sorting of points based on y.
			medianY = aSorter.getMedian().getY(); // Gets the y coordinate of the median point sorted by y.
			
			scanTime = totalTimeX + totalTimeY; // Calculates total time by adding sorting times based on x and y.
			medianCoordinatePoint = new Point(medianX, medianY); // Creates a median coordinate point of mid x and mid y coordinates.
		}		
	}
	
	
	/**
	 * Outputs performance statistics in the format: 
	 * 
	 * <sorting algorithm> <size>  <time>
	 * 
	 * For instance, 
	 * 
	 * selection sort   1000	  9200867
	 * 
	 * Use the spacing in the sample run in Section 2 of the project description. 
	 */
	public String stats() {
		// Outputs more spaces if algorithm name is shorter to line up size.
		if ((sortingAlgorithm == Algorithm.MergeSort) || 
			(sortingAlgorithm == Algorithm.QuickSort) ||
			(sortingAlgorithm == Algorithm.TreeSort)) {
			return aSorter.algorithm + "         " + points.length + "   " + scanTime;
		}
		else if ((sortingAlgorithm == Algorithm.BucketSort) || 
				(sortingAlgorithm == Algorithm.BubbleSort)) {
			return aSorter.algorithm + "       " + points.length + "   " + scanTime;
		}
		else if ((sortingAlgorithm == Algorithm.RadixSort) || 
				(sortingAlgorithm == Algorithm.ShellSort)) {
			return aSorter.algorithm + "        " + points.length + "   " + scanTime;
		}		
		else if (sortingAlgorithm == Algorithm.TimSort) {
			return aSorter.algorithm + "           " + points.length + "   " + scanTime;
		}
		else if ((sortingAlgorithm == Algorithm.HeapSort) || 
				(sortingAlgorithm == Algorithm.CubeSort)) {
			return aSorter.algorithm + "          " + points.length + "   " + scanTime;
		}
		else if (sortingAlgorithm == Algorithm.CountingSort) {
			return aSorter.algorithm + "     " + points.length + "   " + scanTime;
		}		
		return aSorter.algorithm + "    " + points.length + "   " + scanTime;
	}
	
	/**
	 * Write MCP after a call to scan(),  in the format "MCP: (x, y)"   The x and y coordinates of the point are displayed on the same line with exactly one blank space 
	 * in between. 
	 */
	@Override
	public String toString() {
		return "MCP: " + medianCoordinatePoint.toString(); // Calls toString() to avoid code duplication.
	}
	
	/**
	 *  
	 * This method, called after scanning, writes point data into a file by outputFileName. The format 
	 * of data in the file is the same as printed out from toString().  The file can help you verify 
	 * the full correctness of a sorting result and debug the underlying algorithm. 
	 * 
	 * @throws FileNotFoundException
	 */
	public void writeMCPToFile(String outputFileName) throws FileNotFoundException {
		// Writes MCP to existing file using a PrintWriter object.
		try (PrintWriter writer = new PrintWriter(outputFileName)) {
			String mcp = toString();
			writer.println(mcp);
		}
		catch (FileNotFoundException e) {
			throw new FileNotFoundException("Output file " + outputFileName + " not found.");
		}
	}
	
}



