package parser

/**
 * @author eugenio
 */
case class TaskContainers (tToC: Map[String, String], taskOrder: Seq[String]) {
  override def toString = taskOrder map {x => x + "\t" + tToC(x)} mkString "\n"
}
