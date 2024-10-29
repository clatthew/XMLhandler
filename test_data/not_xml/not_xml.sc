import scala.compiletime.ops.double
def sum(a: Int, b: Int): Int = a + b
sum(2, 4)
sum(5, -5)
// val: non-mutable, cannot be reassigned
// var: mutable, can be reassigned
val msg = "Hello"
msg
// msg = "Hallöchen" breaks the worksheet
var greeting = "Hello"
greeting
greeting = "Hallöchen" 
greeting
// Types can be explicit or implicit
val x: Int = 1 // explicit
val y = 2 // implicit
val str = "stringy"
val nums = List(1, 2, 3) // identifies the type of list
// Numeric types
val b: Byte = 1
val i: Int = 1
val l: Long = 1
val s: Short = 1
val d: Double = 2.0
val f: Float = 3.0
// int and double are the default number types.
// The type of number can also be put on the end of a number to specify its type:
val z = 1_000
val a = 1_000L
val c = 3.3F
// When precision is needed, use BigInt and BigDecimal

val firstName = "Matthew"
val middleName = "James"
val lastName = "Clough"
println(s"Name: $firstName $middleName $lastName")
println(s"Age: ${2024-2000}")

if z > 1000 then
    println("quite big")
else if z > 500 then
    println("medium sized")
else
    println("small")



val ages = List(19, 23, 25, 56, 56)
// i <- ages makes a generator then the body of the loops follows do
for i <- ages do println(i + 4)

for 
    i <- ages
    if 20 < i 
    if i < 30
do
    println(i)

for
    i <- 1 to 3
    j <- 'a' to 'c'
    if i == 2
    if j == 'b'
do
    println(s"chosen letters are $i $j")

// scala also has list comprehensions
val doubles0 = for i <- ages yield i * 2
// the following are alternative ways of expressing the above for loop
val doubles1 = for (i <- ages) yield i * 2
val doubles2 = for (i <- ages) yield (i * 2)
val doubles3 = for { i <- ages } yield (i * 2)

val names = List("anna", "matthew", "rebecca", "david", "lucy")
val capNames = for name <- names yield name.capitalize

// better control flow
val result = i match
  case 1 => "one"
  case 2 => "two"
  case _ => "other"
// with arbitrary classes
case class Person(name: String)

def speak(p: Person) = p match {
    case Person(name) if name == "Fred" => println("Yubba dubba doo")
    case Person(name) if name == "Bam Bam" => println("Bam bam!")
    case _ => println("Watch the Flintstones!")
}

speak(Person("Fred"))
speak(Person("Bam Bam"))
speak(Person("Matthew"))
var k = 3
def f(x: Int): Int = x - 1
while k > 0 do k = f(k)
k
k = 3
while
    k > 0
do
    println(k)
    k = f(k)