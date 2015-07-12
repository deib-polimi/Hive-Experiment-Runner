/**
 *
 */
package parser

import scala.io.Source

import java.io.File
import java.io.FileWriter

/**
 * @author Alessandro
 *
 */
object Parser {

    def apply(filename : String) : Durations = {
	    println("Starting " + filename)
	    val lines = Source.fromFile(filename).getLines();//mkString.split("\n");

	    val start = System.currentTimeMillis();
	    val finalStatus = lines.foldLeft(Start : Status)(_ next _);
	    //maps._2.foreach(x => println(x));
	    val stop = System.currentTimeMillis();
	    val i = new File(filename).length;
	    println("Finished in " + ((stop - start).toDouble / 1000) + " s");
	    val ratio = i.toLong * 1000 / (stop-start);
	    println(i + ": " + ratio/1000 + "KB/s")
	    Durations(finalStatus.records);
    }

    def apply(files : Seq[String]) : String = {
	    val durations = files.map(Parser(_));
	    durations.mkString("\n\n") + "\n"
    }

    def parse (path : String): Unit = {
	    val sourceDir = new File (path).getAbsoluteFile;
	    val inputFiles = sourceDir.listFiles().sortBy(_.getName).map(_.getPath)
		    .filter(_.endsWith(".AMLOG.txt")).toSeq;
	    val dataDirectory = new File (sourceDir, "data");
	    dataDirectory.mkdir();

      val durationIn = new File (sourceDir, "appDuration.txt")
	    val durationContent = Source.fromFile (durationIn).mkString;
      val dataDir = new File (sourceDir, "data")
	    val durationOut = new File (dataDir, "appDuration.txt");
	    if (durationOut.exists()) durationOut.delete();
	    val copy = new FileWriter(durationOut);
	    copy.write(durationContent);
	    copy.flush();
	    copy.close();

	    val destFile = new File (dataDir, "taskDuration.txt");
	    if (destFile.exists()) destFile.delete();
	    val out = new FileWriter(destFile);
	    out.write(Parser(inputFiles));
	    out.flush();
	    out.close();
    }

    def main(args: Array[String]): Unit = {
      var directory = "/workspace/RC/5_80_R3/fetched/R3/"
      if (args.length >= 1) directory = args(0)
	    Parser parse directory
    }
}
