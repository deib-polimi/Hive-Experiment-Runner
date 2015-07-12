package parser

/**
 * @author eugenio
 */
case class Sequence (values: Seq[String]) {
  override def toString: String = values mkString "\t"
}
