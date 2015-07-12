/**
 *
 */
package parser

import java.text.SimpleDateFormat
import java.util.Locale

/**
 * @author Alessandro
 *
 */
case class Waiting (values : Map[String, Long]) extends Status (values)
object Start extends Waiting (Map ())
case class Init (name : String, values : Map[String, Long]) extends Status (values)
case class Started (name : String, startTime : Long, endTime : Long,
	                  values : Map[String, Long]) extends Status(values)

abstract class Status (values : Map[String, Long]) {

  protected def parseTime(input : String) =
	  new SimpleDateFormat ("yyyy-MM-dd hh:mm:ss,SSS", Locale.ENGLISH).parse (input).getTime

  def next (line : String) : Status = this match {

    case Waiting (values) => {
	    val name = StatusRegex.init findFirstIn line
	    if (name.isDefined) Init (name.get, values)
	    else this
    }

    case Init (name, values) => {
	    val when = StatusRegex.date findFirstIn line
    	if (when.isDefined) {
        val time = parseTime (when.get)
        Started (name, time, time, values)
      }
	    else this
    }

    case Started (name, start, end, values) => {
	    def updateTime = {
		    val time = StatusRegex.date findFirstIn line
		    if (time.isDefined) Started (name, start, parseTime (time.get), values)
		    else this
	    }
	    if (line.isEmpty) Waiting (values + (name -> (end - start)))
	    else updateTime
    }
  }

  def records = values
}

object StatusRegex {
  val init = """(?<=LogType:syslog_)attempt_\d+_\d+_\d+_\d+_\d+_\d+""".r
  val date = """\d+-\d+-\d+ \d+:\d+:\d+,\d+""".r
}
