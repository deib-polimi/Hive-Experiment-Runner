package parser

/**
 * @author eugenio
 */
case class TaskNodes (cToN: Map[String, String], tToC: Map[String, String],
                      taskOrder: Seq[String]) {
  override def toString = taskOrder map {x => x + "\t" + cToN(tToC(x))} mkString "\n"
}
