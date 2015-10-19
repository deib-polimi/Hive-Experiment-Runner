package parser

import scala.util.matching.Regex

trait StatusRegex {

  val init : Regex
  val date : Regex
  val vertex : Regex
  val taskToVertex : Regex
  val taskToContainer : Regex
  val receivedContainer : Regex
  val startingShuffle : Regex
  val endingShuffle : Regex

}
