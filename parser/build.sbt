lazy val commonSettings = Seq(
  version := "0.0.1",
  scalaVersion := "2.11.6"    
)

lazy val root = (project in file(".")).
  settings(commonSettings: _*).
  settings(
    name := "MapReduce",
    libraryDependencies ++= Seq(
      "org.scala-lang.modules" %% "scala-parser-combinators" % "1.0.3",
      "junit" % "junit" % "4.11",
      "org.scalatest" % "scalatest_2.11" % "2.2.1"
    )
  )

