
package src;

import java.util.ListIterator;

public class test {
	
	
	
	
	public static void main(String[] args) {
		StoutList<String> list = new StoutList<>();
		
		
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();

		list.add("A");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(0);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();

		list.add("A");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();

		list.add("B");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();

		list.add("X");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();

		list.add("Y");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();

		list.add("C");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add("D");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add("E");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(2);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(2);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add("V");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add("W");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add(2, "X");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add(2, "Y");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.add(2, "Z");
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(9);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(3);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(3);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(5);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.remove(3);
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.sort();
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		list.sortReverse();
		System.out.println(list.toStringInternal());
		System.out.println("Size: " + list.size());
		System.out.println();
		
		
		
		
		
	/*
		
		ListIterator<String> iter = list.listIterator(2);	
		System.out.println(list.toStringInternal(iter));
		iter.add("X");
		iter.previous();
		System.out.println(list.toStringInternal(iter));
		iter.add("Y");
		iter.previous();
		System.out.println(list.toStringInternal(iter));
		iter.add("Z");
		System.out.println(list.toStringInternal(iter));
		iter.next();
		iter.next();
		iter.next();
		iter.next();
		iter.next();
		iter.next();
		iter.next();
		iter.remove();
		System.out.println(list.toStringInternal(iter));
		iter.previous();
		iter.previous();
		iter.previous();
		iter.previous();
		iter.previous();
		iter.remove();
		System.out.println(list.toStringInternal(iter));
		iter.next();
		iter.remove();
		System.out.println(list.toStringInternal(iter));
		iter.next();
		iter.next();
		iter.remove();
		System.out.println(list.toStringInternal(iter));
		iter.previous();
		iter.previous();
		iter.remove();
		System.out.println(list.toStringInternal(iter));
*/
		
	}

}














