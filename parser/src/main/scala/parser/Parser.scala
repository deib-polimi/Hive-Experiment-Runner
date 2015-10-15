/**
 *
 */
package parser

import java.io.{File, FileWriter}

import scala.io.Source

/**
 * @author Alessandro
 *
 */
object Parser {

  def apply (filename : String): (StartEnd, Durations, StartEnd, Durations,
    Sequence, VertexListOfTasks, TaskNodes,
    TaskContainers) = {
    println("Starting " + filename)
    val lines = Source.fromFile(filename).getLines();

    val start = System.currentTimeMillis();
    val finalStatus = lines.foldLeft(Start : Status)(_ next _);
    val stop = System.currentTimeMillis();
    val i = new File(filename).length;
    println("Finished in " + ((stop - start).toDouble / 1000) + " s");
    val ratio = i.toLong * 1000 / (stop-start);
    println(i + ": " + ratio/1000 + "KB/s")
    (StartEnd (finalStatus.times), Durations (finalStatus.times),
      StartEnd (finalStatus.shuffleTimes), Durations (finalStatus.shuffleTimes),
      Sequence (finalStatus.vertices),
      VertexListOfTasks (finalStatus.taskToVertices, finalStatus.taskOrder),
      TaskNodes (finalStatus.containerToNodes, finalStatus.taskToContainers,
        finalStatus.taskOrder),
      TaskContainers (finalStatus.taskToContainers, finalStatus.taskOrder))
  }

  def apply (files : Seq[String]): (String, String, String, String, String,
    String, String, String) = {
    val (taskStartEnds, taskDurations, shuffleStartEnds, shuffleDurations,
    vertices, listsOfTasks, taskNodes, taskContainers) =
      files.map (Parser (_))
        .foldLeft ((Seq (): Seq[StartEnd], Seq (): Seq[Durations],
          Seq (): Seq[StartEnd], Seq (): Seq[Durations],
          Seq (): Seq[Sequence], Seq (): Seq[VertexListOfTasks],
          Seq (): Seq[TaskNodes], Seq (): Seq[TaskContainers]))
        {(lists, tuple) => (lists._1 :+ tuple._1, lists._2 :+ tuple._2,
          lists._3 :+ tuple._3, lists._4 :+ tuple._4,
          lists._5 :+ tuple._5, lists._6 :+ tuple._6,
          lists._7 :+ tuple._7, lists._8 :+ tuple._8)}
    (taskStartEnds mkString "\n\n", taskDurations mkString "\n\n",
      shuffleStartEnds mkString "\n\n", shuffleDurations mkString "\n\n",
      vertices mkString "\n", listsOfTasks mkString "\n\n",
      taskNodes mkString "\n\n", taskContainers mkString "\n\n")
  }

  def parse (path : String): Unit = {
    val sourceDir = new File (path).getAbsoluteFile
    val dataDir = new File (sourceDir, "data")
    dataDir.mkdir

    val appDurationIn = new File (sourceDir, "appDuration.txt")
    val appDurationOut = new File (dataDir, "appDuration.txt")
    copyFile(appDurationIn, appDurationOut)

    val inputFiles = sourceDir.listFiles ().sortBy (_.getName)
      .map (_.getPath).filter (_.endsWith (".AMLOG.txt")).toSeq
    val (taskStartEndContent, taskDurationContent, shuffleStartEndContent,
    shuffleDurationContent, verticesContent, listOfTasksContent,
    taskNodesContent, taskContainersContent) = Parser (inputFiles)
    writeToFile (taskStartEndContent, new File (dataDir, "taskStartEnd.txt"))
    writeToFile (taskDurationContent, new File (dataDir, "taskDurationLO.txt"))
    writeToFile (shuffleStartEndContent, new File (dataDir, "shuffleStartEnd.txt"))
    writeToFile (shuffleDurationContent, new File (dataDir, "shuffleDurationLO.txt"))
    writeToFile (verticesContent, new File (dataDir, "vertexOrder.txt"))
    writeToFile (listOfTasksContent, new File (dataDir, "vertexLtask.txt"))
    writeToFile (taskNodesContent, new File (dataDir, "taskNode.txt"))
    writeToFile (taskContainersContent, new File (dataDir, "taskContainer.txt"))
  }

  protected def writeToFile (content: String, file: File): Unit = {
    if (! content.isEmpty) {
      file.delete
      val out = new FileWriter (file)
      out write {
        if (content.last == '\n') content
        else content :+ '\n'
      }
      out.flush
      out.close
    }
  }

  protected def copyFile (from: File, to: File): Unit = {
    val content = Source.fromFile (from).mkString
    to.delete
    val copy = new FileWriter(to)
    copy.write(content)
    copy.flush()
    copy.close()
  }

  def main(args: Array[String]): Unit = {
    var directory = "/workspace/RC/5_80_R3/fetched/R3/"
    if (args.length > 0) directory = args(0)
    Parser parse directory
  }
}
