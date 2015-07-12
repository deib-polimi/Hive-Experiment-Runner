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
case class Waiting (dm : Map[String, Long], vs : Seq[String]) extends Status (dm, vs)
object Start extends Waiting (Map (), Seq())
case class Init (name : String, dm : Map[String, Long], vs : Seq[String])
  extends Status (dm, vs)
case class Started (name : String, startTime : Long, endTime : Long,
	                  dm : Map[String, Long], vs : Seq[String])
  extends Status (dm, vs)

abstract class Status (dm : Map[String, Long], vs : Seq[String]) {

  def durations: Map[String, Long] = dm
  def vertices: Seq[String] = vs

  protected def parseTime(input : String) =
	  new SimpleDateFormat ("yyyy-MM-dd hh:mm:ss,SSS", Locale.ENGLISH).parse (input).getTime

  def next (line : String) : Status = {

	  def nextVertices: Seq[String] = StatusRegex.vertex findFirstMatchIn line match {
	    case Some (m) => vertices :+ (m group 1)
	    case None => vertices
    }

    this match {
      case Waiting (_, _) => {
        val name = StatusRegex.init findFirstIn line
        if (name.isDefined) Init (name.get, durations, nextVertices)
        else Waiting (durations, nextVertices)
      }

      case Init (name, _, _) => {
        val when = StatusRegex.date findFirstIn line
        if (when.isDefined) {
	        val time = parseTime (when.get)
	        Started (name, time, time, durations, nextVertices)
        }
        else Init (name, durations, nextVertices)
      }

      case Started (name, start, end, _, _) => {
        def updateTime = {
	        val time = StatusRegex.date findFirstIn line
	        if (time.isDefined) Started (name, start, parseTime (time.get),
		                                   durations, nextVertices)
	        else this
        }
        if (line.isEmpty) Waiting (durations + (name -> (end - start)), nextVertices)
        else updateTime
      }
    }
  }
}

object StatusRegex {
  val init = """(?<=LogType:syslog_)attempt_\d+_\d+_\d+_\d+_\d+_\d+""".r
  val date = """\d+-\d+-\d+ \d+:\d+:\d+,\d+""".r
  val vertex = """Routing pending task events for vertex: vertex_\d+_\d+_\d+_\d+ \[(.+)\]""".r
}
