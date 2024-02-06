
package src;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;

/**
 * @author Onur Onal
 */

public class TreeDecoder {

	public static void main(String[] args) {
		Scanner scnr = new Scanner(System.in);
		
		System.out.println("Please enter filename to decode: ");
		String fileName = scnr.next();
		
		String encodingScheme = "";
    	String encodedMessage = "";
				
    	// Try-with-resources statement that declares and initializes a BufferedReader wrapped around a FileReader.
        try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
        	String line;
        	int numLine = 0; // Used for counting the number of encoding scheme lines.
        	
        	// Reads all lines from .arch file.
        	while ((line = reader.readLine()) != null) {
        		// Differentiates between the encoding scheme line and the encoded message line.
        		if (line.startsWith("0") || (line.startsWith("1"))) {
        			encodedMessage += line; // Writes line to string variable.
        		}
        		else {
        			// Adds a "\n" in between the two encoding scheme lines.
        			if (numLine > 0) {
        				encodingScheme += "\n";
        			}
        			// Writes line to string variable and increases the number of encoding scheme lines.
        			encodingScheme += line; 
        			numLine++; 
        		}
        	}
        }
        catch (IOException e) {
            System.err.println("Error reading the file: " + e.getMessage());
        }
        finally {
            if (scnr != null) {
                scnr.close();
            }
        }
                        
        // Creates a new binary tree with the encoding scheme from the file.
		MsgTree tree = new MsgTree(encodingScheme);
		        
        System.out.println();
        System.out.println("character code");
        System.out.println("-------------------------");

        // Prints character codes.
        MsgTree.printCodes(tree, ""); 
        
        System.out.println();
        System.out.println("MESSAGE:");

        // Decodes the message.
        tree.decode(tree, encodedMessage);
    }
}

