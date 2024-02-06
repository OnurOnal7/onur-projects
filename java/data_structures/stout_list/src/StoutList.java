
package src;

/**
 *  
 * @author Onur Onal
 *
 */

import java.util.AbstractSequentialList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.ListIterator;
import java.util.NoSuchElementException;

/**
 * Implementation of the list interface based on linked nodes
 * that store multiple items per node.  Rules for adding and removing
 * elements ensure that each node (except possibly the last one)
 * is at least half full.
 */
public class StoutList<E extends Comparable<? super E>> extends AbstractSequentialList<E> {
	/**
	 * Default number of elements that may be stored in each node.
	 */
	private static final int DEFAULT_NODESIZE = 4;
  
	/**
	 * Number of elements that can be stored in each node.
	 */
	private final int nodeSize;
  
	/**
	 * Dummy node for head.  It should be private but set to public here only  
	 * for grading purpose.  In practice, you should always make the head of a 
	 * linked list a private instance variable.  
	 */
	private Node head;
  
	/**
	 * Dummy node for tail.
	 */
	private Node tail;
	
	/*
	 * The current node, i.e the node of operation.
	 */
	private Node current;
	
	/*
	 * The node which the data of "pos" index resides in. Used for adding at specific index and removing.
	 */
	private Node selectedNode;
	
	/**
	 * Number of elements in the list.
	 */
	private int size;
	
	/*
	 * The offset of the current element of the current node.
	 */
	private int offset;
	
	/*
	 * The Comparator that is used in insertionSort.
	 */
	private Comparator<? super E> comp = null;
  
	/**
	 * Constructs an empty list with the default node size.
	 */
	public StoutList() {
		this(DEFAULT_NODESIZE);
	}

	/**
	 * Constructs an empty list with the given node size.
	 * @param nodeSize number of elements that may be stored in each node, must be 
	 *   an even number
	 */
	public StoutList(int nodeSize) {
		if (nodeSize <= 0 || nodeSize % 2 != 0) throw new IllegalArgumentException();
    
		// dummy nodes
		head = new Node();
		tail = new Node();
		head.next = tail;
		tail.previous = head;
		this.nodeSize = nodeSize;
	}
  
	/**
	 * Constructor for grading only.  Fully implemented. 
	 * @param head
	 * @param tail
	 * @param nodeSize
	 * @param size
	 */
	public StoutList(Node head, Node tail, int nodeSize, int size) {
		this.head = head; 
		this.tail = tail;
		this.nodeSize = nodeSize; 
	  	this.size = size; 
	}
	
	/*
	 *  Helper method to find the node at index pos, and set offset at that node.
	 */
	public Node findNode(int pos) {
	    Node node = head.next;
	    Node prevNode = head; // Keeps track of previous node to satisfy condition offset = 0 in add.
	    int numIndex = node.count - 1;
	    
	    // Iterates through nodes, counting number of elements until node with index "pos" is found.
	    while ((numIndex < pos) && (node != tail)) {
	        prevNode = node;
	        node = node.next;
	        numIndex += node.count;
	    }

	    offset = (pos + node.count - 1) - numIndex; // Sets offset of index "pos" in its node.
	    
	    node.previous = prevNode;
	    return node;
	}

	@Override
	public int size() {
		return size;
	}
  
	@Override
	public boolean add(E item) {
		if (item == null) throw new NullPointerException("Cannot add a null item.");
		
		boolean newElement = true;
			
		// Creates the first actual node if there isn't any. Repositions node pointers.
		if ((head.next.equals(tail)) || (tail.previous.equals(head))) {
			current = new Node();
			head.next = current;
			tail.previous = current;
			current.next = tail;
			current.previous = head;
		}
		
		// Creates new node if current node array is full. Repositions node pointers.
		if (current.count >= nodeSize) {
			Node node = new Node();
			current.next = node;
			tail.previous = node;
			node.next = tail;
			node.previous = current;
			current = node;
		}
		
		// Sets boolean based on whether there was a duplicate element.
		if (current.count > 0) {
			if (contains(item)) {
				newElement = false;
			}
		}
		
		// Adds the element at the end of the list.
		current.addItem(item);	
		size++;
		
		return newElement;
	}

	/*
	 *  Helper method to check for duplicate elements in the current node.
	 */
	public boolean contains(E item) {
		for (int i = 0; i < current.count; i++) {
			if (current.data[i].compareTo(item) == 0) {
				return true;
			}
		}
		return false;
	}

	@Override
	public void add(int pos, E item) {
		if (item == null) throw new NullPointerException("Cannot add a null item.");
		
		selectedNode = findNode(pos); // Sets selectedNode to node of index "pos".
		
		// Creates the first actual node if there isn't any. Repositions node pointers.
		if ((head.next.equals(tail)) || (tail.previous.equals(head))) {
			selectedNode = new Node();
			head.next = selectedNode;
			tail.previous = selectedNode;
			selectedNode.next = tail;
			selectedNode.previous = head;
			selectedNode.addItem(0, item);
		}
		else if (offset == 0) {
			// Places "item" at selectedNode's predecessor if there is room and is not the head.
			if ((!selectedNode.previous.equals(head)) && (selectedNode.previous.count < nodeSize)) {
				selectedNode.previous.addItem(item);
			}
			// If selectedNode is full and its predecessor is full, creates a new successor node and adds item to it.
			else if (selectedNode.count == nodeSize) {
				// Defines a successor node that points to its predecessor. 
			    Node successor = new Node();
			    successor.next = selectedNode.next; 
			    successor.previous = selectedNode;
			    
			    if (selectedNode.next != null) {
			        // If there is a node after selectedNode, update its previous reference.
			        selectedNode.next.previous = successor;
			    } 
			    else {
			        tail = successor; // If selectedNode is currently the tail, update the tail reference.
			    }
			    
			    selectedNode.next = successor; // Updates selectedNode's next reference.
			    successor.addItem(0, item); // Adds the item to the new successor node.
			}
			// If there is space even though offset is 0, a regular add is made.
			else {
				selectedNode.addItem(offset, item);
			}
		// Makes regular add at offset if there is space in the node.
		}
		else if (selectedNode.count < nodeSize) {
			selectedNode.addItem(offset, item);
		}
		else {
			// Defines a successor node.
			Node successor = new Node();
			Node temp = selectedNode.next;
			selectedNode.next = successor;
			successor.next = temp;
			
			// Removes items from selectedNode, adding them to successor.
			for (int i = 0; i < nodeSize / 2; i++) {
				successor.addItem(i, selectedNode.data[selectedNode.count - (nodeSize / 2) + i]);
				selectedNode.data[selectedNode.count - (nodeSize / 2) + i] = null;
		    }
			
			selectedNode.count -= (nodeSize / 2); // Updates count for removed items.
						
			// Performs split.
			if (offset <= (nodeSize / 2)) {
				selectedNode.addItem(offset, item);
			}
			else if (offset > (nodeSize / 2)) {
				selectedNode.addItem(offset - (nodeSize / 2), item);
			}
		}
		size++;
	}

	@Override
	public E remove(int pos) {
		if ((pos > (size - 1)) || (pos < 0)) throw new NoSuchElementException("No such element.");
		
		E removed = null; // The removed item.
		
		selectedNode = findNode(pos); // Sets selectedNode to node of index "pos".
		
		// Conditions for a regular remove operation. 
		if (((selectedNode.next.equals(tail)) && (selectedNode.count == 1)) || 
			((selectedNode.next.equals(tail)) || (selectedNode.count > (nodeSize / 2)))) {
			removed = selectedNode.removeItem(offset);
		}
		// Performs merge if half or more of the array is empty.
		else if (selectedNode.count <= (nodeSize / 2)) {
			// Performs mini-merge.
			if (selectedNode.next.count > (nodeSize / 2)) {
				removed = selectedNode.removeItem(offset);
				selectedNode.addItem(selectedNode.next.removeItem(0));
			}
			// Performs full-merge.
			else if (selectedNode.next.count <= (nodeSize / 2)) {
				removed = selectedNode.removeItem(offset);
				int startCount = selectedNode.next.count; // Initial count of the data array of the next node.
				
				// Maps next node data elements to previous node.
				for (int i = 0; i < startCount; i++) {
				    selectedNode.addItem(selectedNode.next.removeItem(0)); 
				}
				selectedNode = selectedNode.next; // Deletes the empty node after full-merge.
			}
		}

		// Removes the empty node if there is one.
		if (selectedNode.count == 0) {
            selectedNode.previous.next = selectedNode.next;
            selectedNode.next.previous = selectedNode.previous;
            selectedNode = null; // Garbage collect selectedNode.
        }
		
		size--;
		return removed;
	}
 
	/**
	 * Sort all elements in the stout list in the NON-DECREASING order. You may do the following. 
	 * Traverse the list and copy its elements into an array, deleting every visited node along 
	 * the way.  Then, sort the array by calling the insertionSort() method.  (Note that sorting 
	 * efficiency is not a concern for this project.)  Finally, copy all elements from the array 
	 * back to the stout list, creating new nodes for storage. After sorting, all nodes but 
	 * (possibly) the last one must be full of elements.  
	 *  
	 * Comparator<E> must have been implemented for calling insertionSort().    
	 */
	public void sort() {
		// 
		E[] elements = toArray();
		this.reset();
		
		setComparator();
		insertionSort(elements, comp);
		
		for (E e : elements) {
			this.add(e);
		}
	}

	/**
	 * Sort all elements in the stout list in the NON-INCREASING order. Call the bubbleSort()
	 * method.  After sorting, all but (possibly) the last nodes must be filled with elements.  
	 *  
	 * Comparable<? super E> must be implemented for calling bubbleSort(). 
	 */
	public void sortReverse() {
		E[] elements = toArray(); // Forms the array using helper method.
		this.reset(); // Deletes nodes, effectively resetting the list.
		
		bubbleSort(elements); // Calls bubblesort.
		
		// Adds sorted elements to list.
		for (E e : elements) {
			this.add(e);
		}
	}
	
	/*
	 * Helper method that forms a generic array of all the elements in the list.
	 */
	public E[] toArray() {
		@SuppressWarnings("unchecked")
		E[] e = (E[]) new Comparable[size]; 
		int index = 0;
		
		Node currNode = head.next;
		
		while (!currNode.equals(tail)) {
			for (int i = 0; i < currNode.count; i++) {
				e[index] = currNode.data[i];
				index++;
			}
			currNode = currNode.next;
		}
		
		return e; 
	}
	
	/*
	 * Helper method that clears the list after filling the generic array.
	 */
	public void reset() {
		head = new Node();
		tail = new Node();
		head.next = tail;
		tail.previous = head;
		size = 0;
	}
  
	@Override
	public Iterator<E> iterator() {
		return new StoutListIterator();
	}

	@Override
	public ListIterator<E> listIterator() {
		return new StoutListIterator();
	}

	@Override
	public ListIterator<E> listIterator(int index) {
		return new StoutListIterator(index);
	}
  
	/**
	 * Returns a string representation of this list showing
	 * the internal structure of the nodes.
	 */
	public String toStringInternal() {
		return toStringInternal(null);
	}

	/**
	 * Returns a string representation of this list showing the internal
	 * structure of the nodes and the position of the iterator.
	 *
	 * @param iter
	 * an iterator for this list
	 */
	public String toStringInternal(ListIterator<E> iter) {
		int count = 0;
		int position = -1;
		if (iter != null) {
			position = iter.nextIndex();
		}

		StringBuilder sb = new StringBuilder();
		sb.append('[');
		Node current = head.next;
		while (current != tail) {
			sb.append('(');
			E data = current.data[0];
			if (data == null) {
				sb.append("-");
			} else {
				if (position == count) {
					sb.append("| ");
					position = -1;
				}
				sb.append(data.toString());
				++count;
			}

			for (int i = 1; i < nodeSize; ++i) {
				sb.append(", ");
				data = current.data[i];
				if (data == null) {
					sb.append("-");
				} else {
					if (position == count) {
						sb.append("| ");
						position = -1;
					}
					sb.append(data.toString());
					++count;

					// iterator at end
					if (position == size && count == size) {
						sb.append(" |");
						position = -1;
					}
				}
			}
			sb.append(')');
			current = current.next;
          	if (current != tail)
              sb.append(", ");
		}
		sb.append("]");
		return sb.toString();
	}


	/**
	 * Node type for this list.  Each node holds a maximum
	 * of nodeSize elements in an array.  Empty slots
 	 * are null.
 	 */
	private class Node {
		/**
		 * Array of actual data elements.
     	*/
		// Unchecked warning unavoidable.
		@SuppressWarnings("unchecked")
		public E[] data = (E[]) new Comparable[nodeSize];
    
		/**
		 * Link to next node.
		 */
		public Node next;
    
		/**
		 * Link to previous node;
		 */
		public Node previous;
    
		/**
		 * Index of the next available offset in this node, also 
		 * equal to the number of elements in this node.
		 */
		public int count;

		/**
		 * Adds an item to this node at the first available offset.
		 * Precondition: count < nodeSize
		 * @param item element to be added
		 */
		void addItem(E item) {
			if (count >= nodeSize) {
				return;
			}
			data[count++] = item;
			// useful for debugging
			// System.out.println("Added " + item.toString() + " at index " + count + " to node "  + Arrays.toString(data));
		}
  
		/**
		* Adds an item to this node at the indicated offset, shifting
		* elements to the right as necessary.
     	* Precondition: count < nodeSize
     	* @param offset array index at which to put the new element
     	* @param item element to be added
     	*/
		void addItem(int offset, E item) {
			if (count >= nodeSize) {
				return;
			}
			for (int i = count - 1; i >= offset; --i) {
				data[i + 1] = data[i];
			}
			++count;
			data[offset] = item;
			// useful for debugging 
			// System.out.println("Added " + item.toString() + " at index " + offset + " to node: "  + Arrays.toString(data));
		}

		/**
		 * Deletes an element from this node at the indicated offset, 
		 * shifting elements left as necessary.
		 * Precondition: 0 <= offset < count
		 * @param offset
		 */
		E removeItem(int offset) {
			E item = data[offset];
			for (int i = offset + 1; i < nodeSize; ++i) {
				data[i - 1] = data[i];
			}
			data[count - 1] = null;
			--count;
			
			return item;
		}    
	}
 
	private class StoutListIterator implements ListIterator<E> {
		
		private Node current; // The node of operation.
		private int index; // The cursor position.
		private int offset; // The offset of "current".
		
		private static final int AHEAD = 0; // Static value that allows to delete and set ahead of updated cursor.
		private static final int BEHIND = -1; // Static value that allows to delete and set behind of updated cursor.
		private int direction = 1; // Direction set to either AHEAD or BEHIND. Initially set at neutral value to indicate no direction.
			
		/**
		 * Default constructor 
		 */
		public StoutListIterator() {
			current = head.next;
			index = 0;
		}

		/**
		 * Constructor finds node at a given position.
     	* @param pos
     	*/
		public StoutListIterator(int pos) {
			if ((pos < 0) || (pos > size)) throw new IllegalArgumentException("Position out of range");
			
			current = findNode(pos);
			index = pos;
		}
		
		/*
		 *  Helper method to find the node at index pos, and set offset at that node.
		 */
		public Node findNode(int pos) {
		    Node node = head.next;
		    Node prevNode = head; // Keeps track of previous node to satisfy condition offset = 0 in add.
		    int numIndex = node.count - 1;
		    
		    // Iterates through nodes, counting number of elements until node with index "pos" is found.
		    while ((numIndex < pos) && (node != tail)) {
		        prevNode = node; 
		        node = node.next;
		        numIndex += node.count;
		    }

		    offset = (pos + node.count - 1) - numIndex; // Sets offset of index "pos" in its node.
		    
		    node.previous = prevNode;
		    return node;
		}

		@Override
		public boolean hasNext() {
			return index < size;		
		}

		@Override
		public E next() {
			if (index >= size) throw new NoSuchElementException("No such element.");
			
			// Moves cursor forward and sets direction.
			index++;
			direction = BEHIND;
			
			// Moves to succeeding node if cursor points to the last element of the current node, 
			// and if the current node has more than one element.
			if ((offset >= (current.count - 1)) && (current.count > 1)) {
				Node node = current.next;
				current = node;
				offset = 0;
			}
			else {
				offset++;
			}	
			
			return current.data[offset]; // Returns the element succeeding the one that the cursor points to.
		}

		@Override
		public void remove() {
			if ((index > (size - 1)) || (index < 0)) throw new NoSuchElementException("No such element.");
			
			current = findNode(index); // Sets current to node of index "pos".
			
			// Conditions for a regular remove operation. 
			if (((current.next.equals(tail)) && (current.count == 1)) || 
				((current.next.equals(tail)) || (current.count > (nodeSize / 2)))) {
				
				// Removes last element of the node if next() is called at the end of a node.  
				if ((direction == BEHIND) && (offset == 0)) {
					current.removeItem(offset);
					current = current.previous;
					current.next = tail;
					tail.previous = current;
				}
				else {
					current.removeItem(offset + direction);
				}
				
				offset = current.previous.count - 1;
			}
			// Performs merge if half or more of the array is empty.
			else if (current.count <= (nodeSize / 2)) {
				// Performs mini-merge.
				if (current.next.count > (nodeSize / 2)) {
					if ((direction == BEHIND) && (offset == 0)) {
						current.removeItem(offset);
					}
					else {
						current.removeItem(offset + direction);
					}	
					
					current.addItem(current.next.removeItem(0));
					index++; // Position of cursor is not changed if mini-merge occurs.
				}
				// Performs full-merge.
				else if (current.next.count <= (nodeSize / 2)) {
					if ((direction == BEHIND) && (offset == 0)) {
						current.removeItem(offset);
					}
					else {
						current.removeItem(offset + direction);
					}
					
					int startCount = current.next.count; // Initial count of the data array of the next node.
					
					// Maps next node data elements to previous node.
					for (int i = 0; i < startCount; i++) {
						current.addItem(current.next.removeItem(0));
					}
					current = current.next; // Deletes the empty node after full-merge.
				}
			}

			// Removes the empty node if there is one.
			if (current.count == 0) {
				current.previous.next = current.next;
				current.next.previous = current.previous;
				current = null; // Garbage collect selectedNode.
	        }
			direction = 1; // Sets direction to none. Cannot call set() after an item is added.
			index--; // Updates the cursor position. 
			size--;
		}

		@Override
		public boolean hasPrevious() {
			return index > 0;
		}

		@Override
		public E previous() {
			if (index <= 0) throw new NoSuchElementException("No such element.");
			
			// Moves cursor backward and sets direction.
			index--;
			direction = AHEAD;
			
			// Moves to preceding node if cursor points to the first element of the current node.
			if (offset <= 0) {
				Node node = current.previous;
				current = node;
				offset = current.count - 1;
			}
			else {
				offset--;
			}
			
			return current.data[offset]; // Returns the element preceding the one that the cursor points to.
		}
		
		@Override
		public int nextIndex() {
			return index;
		}

		@Override
		public int previousIndex() {
			return index - 1;
		}

		@Override
		public void set(E e) {
			// Direction of traversion must be specified beforehand. 
			if ((direction != AHEAD) && (direction != BEHIND)) throw new IllegalStateException("Direction of iteration not specified.");

			// Sets last element of the node if next() is called at the end of a node.  
			if ((direction == BEHIND) && (offset == 0)) {
				current.previous.data[current.previous.count - 1] = e;
			}
			else {
				current.data[offset + direction] = e; // Sets the element based on the direction.
			}
		}
		
		@Override
		public void add(E e) {
			if (e == null) throw new NullPointerException("Cannot add a null item.");
			
			current = findNode(index);	// Sets current to node of index "pos".	
			
			// Creates the first actual node if there isn't any. Repositions node pointers.
			if ((head.next.equals(tail)) || (tail.previous.equals(head))) {
				current = new Node();
				head.next = current;
				tail.previous = current;
				current.next = tail;
				current.previous = head;
				current.addItem(0, e);
			}
			// Places "item" at selectedNode's predecessor if there is room and is not the head.
			else if (offset == 0) {
				if ((!current.previous.equals(head)) && (current.previous.count < nodeSize)) {
					current.previous.addItem(e);
				}
				// If selectedNode is full and its predecessor is full, creates a new successor node and adds item to it.
				else if (current.count == nodeSize) {
					// Defines a successor node that points to its predecessor. 
				    Node successor = new Node();
				    successor.next = current.next; 
				    successor.previous = current;
				    
				    if (current.next != null) {
				        // If there is a node after selectedNode, update its previous reference.
				    	current.next.previous = successor;
				    } 
				    else {
				        tail = successor; // If selectedNode is currently the tail, update the tail reference.
				    }
				    current.next = successor; // Updates selectedNode's next reference.
				    successor.addItem(0, e); // Adds the item to the new successor node.
				}
				// If there is space even though offset is 0, a regular add is made.
				else {
					current.addItem(offset, e);
				}
			// Makes regular add at offset if there is space in the node.
			}
			else if (current.count < nodeSize) {
				current.addItem(offset, e);
			}
			else {
				// Defines a successor node.
				Node successor = new Node();
				Node temp = current.next;
				current.next = successor;
				successor.next = temp;
				
				// Removes items from selectedNode, adding them to successor.
				for (int i = 0; i < nodeSize / 2; i++) {
					successor.addItem(i, current.data[current.count - (nodeSize / 2) + i]);
					current.data[current.count - (nodeSize / 2) + i] = null;
			    }
				
				current.count -= (nodeSize / 2); // Updates count for removed items.
							
				// Performs split.
				if (offset <= (nodeSize / 2)) {
					current.addItem(offset, e);
				}
				else if (offset > (nodeSize / 2)) {
					current.addItem(offset - (nodeSize / 2), e);
				}
				
				// Cursor remains in the current node after split.
				index--;
				offset--;
			}
			direction = 1; // Sets direction to none. Cannot call set() after an item is added.
			index++; // Updates the cursor position. 
			size++; 
		}
	}

	/**
	 * Sort an array arr[] using the insertion sort algorithm in the NON-DECREASING order. 
	 * @param arr   array storing elements from the list 
	 * @param comp  comparator used in sorting 
	 */
	private void insertionSort(E[] arr, Comparator<? super E> comp) {
		int size = arr.length;
		E temp;
		
		for (int i = 1; i < size; i++) {
			temp = arr[i];
			int j = i - 1;
			
			// Uses compare method of comparator to compare elements.
			while ((j > -1) && (comp.compare(arr[j], temp)) > 0) {
				arr[j + 1] = arr[j];
				j--;
			}
			arr[j + 1] = temp;
		}
	}
  
	/**
	* Sort arr[] using the bubble sort algorithm in the NON-INCREASING order. For a 
   	* description of bubble sort please refer to Section 6.1 in the project description. 
   	* You must use the compareTo() method from an implementation of the Comparable 
   	* interface by the class E or ? super E. 
   	* @param arr  array holding elements from the list
   	*/
	private void bubbleSort(E[] arr) {
		int size = arr.length;
		boolean swapped;
		
		do {
            swapped = false;
            for (int i = 1; i < size; i++) {
				// Sorts in non-incresing order by using "<" instead of ">".
                if (arr[i - 1].compareTo(arr[i]) < 0) {
                    E temp = arr[i - 1];
                    arr[i - 1] = arr[i];
                    arr[i] = temp;
                    swapped = true;
                }
            }
        } while (swapped);
	}
	
	/*
	 * Method that sets the comparator to be used in insertionSort.
	 */
	private void setComparator() {
		// Inner class sets comparator to compare two generic values.
		comp = new Comparator<E>() {
			@Override
			public int compare(E a, E b) {
				return a.compareTo(b);
			}
		};
	}
 

}



