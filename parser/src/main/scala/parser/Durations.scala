/**
 *
 */
package parser

/**
 * @author Alessandro
 *
 */
case class Durations(values : Map[String, Long]) {
  
  override def toString = values.map{case (k,v) => k + "\t" +v}.mkString("\n");

}