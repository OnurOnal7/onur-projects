
package src;

import java.util.Stack;

/**
 * @author Onur Onal
 */

public class MsgTree {

    public char payloadChar;
    public MsgTree left;
    public MsgTree right;
    
    /*
     * Constructor iteratively constructs a preorder binary tree using an explicit stack.
     */
    public MsgTree(String encodingString) {
    	// Creates a stack of type node to store internal nodes.
    	Stack<MsgTree> nodes = new Stack<MsgTree>();
    	
    	// Defines node variables for the root node and current node of operation.
    	MsgTree root = null;
    	MsgTree current = null;
    	
    	// Iteratates through the character array of the encoded string.
    	for (char c : encodingString.toCharArray()) {
    		if (c != '^') {
    			// Creates a new leaf node using the second constructor.
    			MsgTree leaf = new MsgTree(c);
    			
    			// Sets the root node to the leaf node if the stack is empty (No internal nodes have been processed yet)
    			if (nodes.isEmpty()) {
    				root = leaf;
    			}
    			else {
    				// Sets the leaf node as the appropriate child of the current node.
    				if (current.left == null) {
    					current.left = leaf;
    				}
    				else {
    					current.right = leaf;
    				}
    			}
    		}
    		else {
    			// Creates a new internal node using the second constructor.
    			MsgTree internal = new MsgTree('^');
    			
    			// Sets the root node to the internal node if the stack is empty (No internal nodes have been processed yet)
    			if (nodes.isEmpty()) {
    				root = internal;
    			}
    			else {
    				// Sets the internal node as the appropriate child of the current node.
    				if (current.left == null) {
    					current.left = internal;
    				}
    				else {
    					current.right = internal;
    				}
    			}
    			
    			// Pushes the current internal node onto the stack to "remember" that child nodes will be connected to this internal node.
    			nodes.push(internal);
    		}
    		
    		// Uses backtracking to "stop remembering" the current internal node after both of its children have been processed.
    		while ((!nodes.isEmpty()) && (nodes.peek().right != null)) {
    			nodes.pop();
    		}
    		
    		// Sets the current node to the internal node before the node that just finished processing its children.
    		if (!nodes.isEmpty()) {
    			current = nodes.peek();
    		}
    	}
    	
    	// Sets the character and children of the root node.
		this.payloadChar = root.payloadChar;
		this.left = root.left;
		this.right = root.right;
    }
  
    /*
     * Constructor builds a single node with null children.
     */
    public MsgTree(char payloadChar) {
    	this.payloadChar = payloadChar;
        this.left = null;
        this.right = null;
    }
    
    /*
     * Prints the binary code of each character in the encoding scheme.
     */
    public static void printCodes(MsgTree root, String code) {
        if (root != null) {
        	// Does not print code for internal nodes.
            if (root.payloadChar != '^') {
                String currPayloadChar;

                // Conditional to ensure that new lines are printed as "\n" rather than an actual new line.
                if (root.payloadChar == '\n') {
                    currPayloadChar = "\\n";
                }
                else {
                    currPayloadChar = String.valueOf(root.payloadChar);
                }

                // Prints character of current node along with its code.
                System.out.println(currPayloadChar + " " + code);
            }

            // Performs recursive preorder traversal, same as the order with which the tree was created.
            printCodes(root.left, code + "0");
            printCodes(root.right, code + "1");
        }
    }

    /*
     * Prints the characters corresponding to the codes within the encoded message.
     */
    public void decode(MsgTree root, String msg) {
        MsgTree current = root;
        
        // Traverses each bit in the encoded message.
        for (char bit : msg.toCharArray()) {
        	// Follows the path of the sequence of bits to find the correct node.
            if (bit == '0') {
                current = current.left;
            } else if (bit == '1') {
                current = current.right;
            }

            // Only prints characters at leaf nodes.
            if ((current != null) && (current.left == null) && (current.right == null)) {
                System.out.print(current.payloadChar);
                current = root; // Returns to the root node.
            }
        }
    }
}

