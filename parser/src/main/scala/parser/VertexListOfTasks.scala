package parser

/**
 * @author eugenio
 */
case class VertexListOfTasks (couples: Map[String, Seq[String]],
                              taskOrder: Seq[String]) {
  override def toString = lines mkString "\n"

  def lines = for (mapping <- couples) yield {
    val (key, list) = mapping
    val currentTasks = taskOrder filter {x => list contains x}
    key +: currentTasks mkString "\t"
  }
}
