/**
 *
 */
package parser

/**
 * @author Alessandro
 *
 */
case class Durations (values : Map[String, (Long, Long)]) {
  override def toString = values map {case (k,v) =>
    k + "\t" + (v._2 - v._1)} mkString "\n"
}
