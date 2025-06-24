import java.io.FileNotFoundException;

public class Main {
    public static void main(String[] args) throws FileNotFoundException {
        GephiVis gephiVis = new GephiVis();
        System.out.println("Layout duration: " + args[0]);
        System.out.println("Input file: " + args[1]);
        System.out.println("Network file: " + args[2]);
        System.out.println("Reprocess All: " + args[3]);
        
        gephiVis.script(Integer.parseInt(args[0]), args[1], args[2], args[2]);
        System.exit(0);
    }
}