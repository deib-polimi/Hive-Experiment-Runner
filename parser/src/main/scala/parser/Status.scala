/**
 *
 */
package parser

import java.text.SimpleDateFormat
import java.util.Locale
import java.util.NoSuchElementException

/**
 * @author Alessandro
 *
 */
case class Waiting (tm : Map[String, (Long, Long)], vs : Seq[String],
                    tv : Map[String, Seq[String]], tc : Map[String, String],
                    to : Seq[String], cn : Map[String, String],
                    stm : Map[String, (Long, Long)])
  extends Status (tm, vs, tv, tc, to, cn, stm)

object Start extends Waiting (Map(), Seq(), Map(), Map(), Seq(), Map(), Map())

case class Init (name : String, tm : Map[String, (Long, Long)], vs : Seq[String],
                 tv : Map[String, Seq[String]], tc : Map[String, String],
                 to : Seq[String], cn : Map[String, String],
                 stm : Map[String, (Long, Long)])
  extends Status (tm, vs, tv, tc, to, cn, stm)

case class Started (name : String, startTime : Long, endTime : Long,
	                  tm : Map[String, (Long, Long)], vs : Seq[String],
                    tv : Map[String, Seq[String]], tc : Map[String, String],
                    to : Seq[String], cn : Map[String, String],
                    stm : Map[String, (Long, Long)])
  extends Status (tm, vs, tv, tc, to, cn, stm)

case class Shuffling (name : String, startTask : Long, endTask : Long,
                      startShuffle : Long, tm : Map[String, (Long, Long)],
                      vs : Seq[String], tv : Map[String, Seq[String]],
                      tc : Map[String, String], to : Seq[String],
                      cn : Map[String, String], stm : Map[String, (Long, Long)])
  extends Status (tm, vs, tv, tc, to, cn, stm)

abstract class Status (tm : Map[String, (Long, Long)], vs : Seq[String],
                       tv : Map[String, Seq[String]], tc : Map[String, String],
                       to : Seq[String], cn : Map[String, String],
                       stm : Map[String, (Long, Long)]) {

  def times: Map[String, (Long, Long)] = tm
  def vertices: Seq[String] = vs
  def taskToVertices: Map[String, Seq[String]] = tv
  def taskToContainers: Map[String, String] = tc
  def taskOrder: Seq[String] = to
  def containerToNodes: Map[String, String] = cn
  def shuffleTimes: Map[String, (Long, Long)] = stm

  protected def parseTime(input : String) =
	  new SimpleDateFormat ("yyyy-MM-dd HH:mm:ss,SSS", Locale.ENGLISH).parse (input).getTime

  def next (line : String) : Status = {

	  def nextVertices: Seq[String] = StatusRegex.vertex findFirstMatchIn line match {
	    case Some (m) => vertices :+ (m group 1)
	    case None => vertices
    }

    def nextTaskToVertices: Map[String, Seq[String]] =
      StatusRegex.taskToVertex findFirstMatchIn line match {
      case Some (m) => {
        val (vertex, task) = (m group 1, m group 2)
        if (taskToVertices contains vertex) {
          val nextSeq = taskToVertices (vertex) :+ task
          taskToVertices + (vertex -> nextSeq)
        }
        else {
          val nextSeq = Seq (task)
          taskToVertices + (vertex -> nextSeq)
        }
      }
      case None => taskToVertices
    }

    def nextTaskToContainers: Map[String, String] =
      StatusRegex.taskToContainer findFirstMatchIn line match {
      case Some (m) => {
        val (task, container) = (m group 1, m group 2)
        taskToContainers + (task -> container)
      }
      case None => taskToContainers
    }

    def nextTaskOrder: Seq[String] =
      StatusRegex.taskToContainer findFirstMatchIn line match {
      case Some (m) => taskOrder :+ (m group 1)
      case None => taskOrder
    }

    def nextContainerToNodes: Map[String, String] =
      StatusRegex.receivedContainer findFirstMatchIn line match {
      case Some (m) => {
        val (container, node) = (m group 1, m group 2)
        containerToNodes + (container -> node)
      }
      case None => containerToNodes
    }

    this match {
      case Waiting (_, _, _, _, _, _, _) => {
        val name = StatusRegex.init findFirstIn line
        if (name.isDefined) Init (name.get, times, nextVertices, nextTaskToVertices,
                                  nextTaskToContainers, nextTaskOrder,
                                  nextContainerToNodes, shuffleTimes)
        else Waiting (times, nextVertices, nextTaskToVertices,
                      nextTaskToContainers, nextTaskOrder,
                      nextContainerToNodes, shuffleTimes)
      }

      case Init (name, _, _, _, _, _, _, _) => {
        val when = StatusRegex.date findFirstIn line
        if (when.isDefined) {
	        val time = parseTime (when.get)
	        Started (name, time, time, times, nextVertices, nextTaskToVertices,
                   nextTaskToContainers, nextTaskOrder,
                   nextContainerToNodes, shuffleTimes)
        }
        else Init (name, times, nextVertices, nextTaskToVertices,
                   nextTaskToContainers, nextTaskOrder,
                   nextContainerToNodes, shuffleTimes)
      }

      case Started (name, start, end, _, _, _, _, _, _, _) => {
	      def lookForShuffle = {
		      def updateTime = {
			      val time = StatusRegex.date findFirstIn line
				    if (time.isDefined) Started (name, start, parseTime (time.get),
					                               times, nextVertices, nextTaskToVertices,
					                               nextTaskToContainers, nextTaskOrder,
					                               nextContainerToNodes, shuffleTimes)
					  else Started (name, start, end, times, nextVertices,
                          nextTaskToVertices, nextTaskToContainers,
                          nextTaskOrder, nextContainerToNodes, shuffleTimes)
		      }
          StatusRegex.startingShuffle findFirstMatchIn line match {
            case Some (_) => {
              val time = parseTime ((StatusRegex.date findFirstIn line).get)
              Shuffling (name, start, time, time, times, nextVertices,
                         nextTaskToVertices, nextTaskToContainers,
                         nextTaskOrder, nextContainerToNodes, shuffleTimes)
            }
            case None => updateTime
          }
	      }
        if (line.isEmpty) Waiting (times + (name -> (start, end)), nextVertices,
                                   nextTaskToVertices, nextTaskToContainers,
                                   nextTaskOrder, nextContainerToNodes,
                                   shuffleTimes)
        else lookForShuffle
      }

      case Shuffling (name, startTask, endTask, startShuffle,
                      _, _, _, _, _, _, _) => {
        def updateTime = {
          val time = StatusRegex.date findFirstIn line
          if (time.isDefined) Shuffling (name, startTask, parseTime (time.get),
                                         startShuffle, times, nextVertices,
                                         nextTaskToVertices, nextTaskToContainers,
                                         nextTaskOrder, nextContainerToNodes,
                                         shuffleTimes)
          else Shuffling (name, startTask, endTask, startShuffle, times,
                          nextVertices, nextTaskToVertices, nextTaskToContainers,
                          nextTaskOrder, nextContainerToNodes, shuffleTimes)
        }
        StatusRegex.endingShuffle findFirstMatchIn line match {
          case Some (_) => {
            val time = parseTime ((StatusRegex.date findFirstIn line).get)
            Started (name, startTask, time, times, nextVertices,
                     nextTaskToVertices, nextTaskToContainers, nextTaskOrder,
                     nextContainerToNodes,
                     shuffleTimes + (name -> (startShuffle, time)))
          }
          case None => updateTime
        }
      }
    }
  }
}

object StatusRegex {
  val init = """(?<=LogType:syslog_)attempt_\d+_\d+_\d+_\d+_\d+_\d+""".r
  val date = """\d+-\d+-\d+ \d+:\d+:\d+,\d+""".r
  val vertex = """Routing pending task events for vertex: vertex_\d+_\d+_\d+_\d+ \[(.+)\]""".r
  val taskToVertex = """impl.TaskAttemptImpl: remoteTaskSpec:DAGName.+VertexName: (.+), VertexParallelism.+TaskAttemptID:(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+)""".r
  val taskToContainer = """Assigned taskAttempt.+(attempt_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+_[0-9]+).+to container:.+(container_[0-9]+_[0-9]+_[0-9]+_[0-9]+)""".r
  val receivedContainer = """Assigning container to task, container=Container: \[ContainerId: (container_[0-9]+_[0-9]+_[0-9]+_[0-9]+).* containerHost=(\w+)""".r
  val startingShuffle = """orderedgrouped.Shuffle: Shuffle assigned with""".r
  val endingShuffle = """orderedgrouped.Shuffle: Shutting down Shuffle for source""".r
}
