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
    println("Finished in " + (stop-start)/1000);
    val ratio = i.toLong *1000 / (stop-start);
    println(i + ": " + ratio/1000 + "KB/s") 
    Durations(finalStatus.records);        
  }
  
  def apply(files : Seq[String]) : String = {
    val durations = files.map(Parser(_));
    durations.mkString("\n\n");
  }
  
  def parseDirectory(path : String) = {
    val sourceDir = new File(path);
    val inputFiles = sourceDir.listFiles().sortBy(_.getName).map(_.getPath).filter(_.endsWith(".AMLOG.txt")).toSeq;
    val dataDirectory = new File(path+"/data");
    dataDirectory.mkdir();  
    
    
    val durationContent = Source.fromFile(path + "appDuration.txt").mkString;
    val durationFile = new File(path + "/data/appDuration.txt");
    if(durationFile.exists()) durationFile.delete();
    val copy = new FileWriter(durationFile); 
    copy.write(durationContent);
    copy.flush();
    copy.close();
    
    val destFile = new File(path + "/data/taskDuration.txt");
    if(destFile.exists()) destFile.delete();
    val out = new FileWriter(destFile);    
    
      
    out.write(Parser(inputFiles));
    out.flush();
    out.close();
  }
  
  def main(args: Array[String]): Unit = {
    Parser.parseDirectory("/workspace/RC/5_80_R3/fetched/R3/");
  }
  
  

}

