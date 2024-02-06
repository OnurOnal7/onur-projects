
package src;

/**
 *  
 * @author Onur Onal
 *
 */

/**
 * 
 * This class implements the tree sort algorithm.   
 *
 */

public class TreeSorter extends AbstractSorter
{

	// Other private instance variables if needed
	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public TreeSorter(Point[] pts) {
		super(pts);
		algorithm = "tree sort";
	}


	/**
	 * Perform tree sort on the array points[] of the parent class AbstractSorter. 
	 * 
	 */
	@Override
    public void sort() {
        TreeNode root = null;
        for (Point point : points) {
            root = insert(root, point);
        }
        
        inOrderTraversal(root, 0);
    }

    // Definition for a binary tree node
    private class TreeNode {
        Point point;
        TreeNode left, right;

        TreeNode(Point point) {
            this.point = point;
            this.left = this.right = null;
        }
    }

    // Function to insert a new node into the binary tree
    private TreeNode insert(TreeNode root, Point point) {
        if (root == null) {
            root = new TreeNode(point);
            return root;
        }

        // Compare and insert in the appropriate subtree
        if (pointComparator.compare(point, root.point) < 0) {
            root.left = insert(root.left, point);
        } 
        else {
            root.right = insert(root.right, point);
        }

        return root;
    }

    // In-order traversal to populate the sorted array
    private void inOrderTraversal(TreeNode root, int index) {
        if (root != null) {
            inOrderTraversal(root.left, index);
            points[index] = root.point;
            index++;
            inOrderTraversal(root.right, index);
        }
    }

	





}





