package parser

/**
 * @author eugenio
 */
case class StartEnd (values: Map[String, (Long, Long)]) {
  override def toString = values map {case (k, v) => k + "\t" + v._1 + "\t" +
    v._2} mkString "\n"
}
