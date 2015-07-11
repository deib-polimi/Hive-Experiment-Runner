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
abstract class Status(values : Map[String, Long]) {
  
  protected val dateRegexp = """\d+-\d+-\d+ \d+:\d+:\d+,\d+""".r;
  
  protected def parseTime(input : String) = 
    new SimpleDateFormat("yyyy-MM-dd hh:mm:ss,SSS", Locale.ENGLISH).parse(input).getTime;  
  
  def next(line : String) : Status; 
  
  def records = values;

}

case class Waiting(values : Map[String, Long]) extends Status(values){
  
  private val init = """(?<=LogType:syslog_)attempt_\d+_\d+_\d+_\d+_\d+_\d+""".r;
  
  override def next(line : String) : Status = {
      val name = init.findFirstIn(line);
      if(name.isDefined) Init(name.get, values);
      else this;
  }
        
}

object Start extends Waiting(Map());

case class Init(name : String, values : Map[String, Long]) extends Status(values){
  
  override def next(line : String) : Status = {
    val time = dateRegexp.findFirstIn(line);
    if(time.isDefined) Started(name, parseTime(time.get), parseTime(time.get), values);
    else this;    
  }
    
  
}
case class Started(name : String, startTime : Long, endTime : Long, values : Map[String, Long])
  extends Status(values){
  

  override def next(line : String) : Status = {
    def updateTime = {
      val time = dateRegexp.findFirstIn(line);
      if(time.isDefined) Started(name, startTime, parseTime(time.get), values);
      else this;
    }
    if(line.isEmpty) Waiting(values + (name -> (endTime -startTime)));
    else updateTime;        
  }
  
}
