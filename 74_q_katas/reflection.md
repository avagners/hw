# Квантовые вычисления

## Задача 1. Powers of Imaginary Unit

Input: An even integer 
. The integer can be zero, positive or negative, but it is guaranteed to be even.

Goal: Return i^n , that is, the n-th power of i.

Решение:
```q#
namespace Kata {
    function EvenPowerOfI(n : Int) : Int {
        if n % 4 == 0 {
            return 1;
        } else {
            return -1;
        }
   }
}
```

## Задача 2. Add Complex Numbers

Inputs:

1. A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>x</mi>
  <mo>=</mo>
  <mi>a</mi>
  <mo>+</mo>
  <mi>b</mi>
  <mi>i</mi>
</math>

2. A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>y</mi>
  <mo>=</mo>
  <mi>c</mi>
  <mo>+</mo>
  <mi>d</mi>
  <mi>i</mi>
</math>

Goal: Return the sum of x and y as a complex number.

Решение:
```q#
namespace Kata {
    import Std.Math.*;

    function ComplexAdd(x : Complex, y : Complex) : Complex {
        let (a, b) = (x.Real, x.Imag);
        let (c, d) = (y.Real, y.Imag);
        return Complex(a + c, b + d);
    }
}
```

## Задача 3. Multiply Complex Numbers

Inputs:

1. A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>x</mi>
  <mo>=</mo>
  <mi>a</mi>
  <mo>+</mo>
  <mi>b</mi>
  <mi>i</mi>
</math>

2. A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>y</mi>
  <mo>=</mo>
  <mi>c</mi>
  <mo>+</mo>
  <mi>d</mi>
  <mi>i</mi>
</math>

Goal: Return the product of x and y as a complex number.

Решение:
```q#
namespace Kata {
    import Std.Math.*;

    function ComplexMult(x : Complex, y : Complex) : Complex {
        let (a, b) = (x.Real, x.Imag);
        let (c, d) = (y.Real, y.Imag);
        return Complex(a * c - b * d, a * d + b * c);
    }
}
```

## Задача 4. Find Conjugate

Input: A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>x</mi>
  <mo>=</mo>
  <mi>a</mi>
  <mo>+</mo>
  <mi>b</mi>
  <mi>i</mi>
</math>.

Goal: Return the complex conjugate of x <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mover>
    <mi>x</mi>
    <mo accent="true">&#x2015;</mo>
  </mover>
  <mo>=</mo>
  <mi>a</mi>
  <mo>&#x2212;</mo>
  <mi>b</mi>
  <mi>i</mi>
</math>.

Решение: 
```q#
namespace Kata {
    import Std.Math.*;

    function ComplexConjugate(x : Complex) : Complex {
        Complex(x.Real, -x.Imag)
    }
}
```

## Задача 5. Divide Complex Numbers

Inputs:

1. A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>x</mi>
  <mo>=</mo>
  <mi>a</mi>
  <mo>+</mo>
  <mi>b</mi>
  <mi>i</mi>
</math>.

2. A complex number <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mi>y</mi>
  <mo>=</mo>
  <mi>c</mi>
  <mo>+</mo>
  <mi>d</mi>
  <mi>i</mi>
  <mo>&#x2260;</mo>
  <mn>0</mn>
</math>.

Goal: Return the result of the division <math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac>
    <mi>x</mi>
    <mi>y</mi>
  </mfrac>
  <mo>=</mo>
  <mfrac>
    <mrow>
      <mi>a</mi>
      <mo>+</mo>
      <mi>b</mi>
      <mi>i</mi>
    </mrow>
    <mrow>
      <mi>c</mi>
      <mo>+</mo>
      <mi>d</mi>
      <mi>i</mi>
    </mrow>
  </mfrac>
</math>.

Решение: 
```q#
namespace Kata {
    import Std.Math.*;

    function ComplexDiv(x : Complex, y : Complex) : Complex {
        let (a, b) = (x.Real, x.Imag);
        let (c, d) = (y.Real, y.Imag);
        let denominator = c * c + d * d;
        let real = (a * c + b * d) / denominator;
        let imag = (- a * d + b * c) / denominator;
        return Complex(real, imag);
    }
}
```

## Выводы

Из-за ограниченного времени я выбрал первые 5 задач из раздела "Learn with Microsoft Quantum katas", которые охватывали базовые математические операции с комплексными числами.

Тема крайне интересная.
Для глубокого понимания нужно значительно больше времени. 

Хотя выполненные задачи кажутся простыми (это была лишь "разминка"), они дали важное - понимание, с чего начинать. 

Комплексные числа - это фундамент, и без них двигаться дальше нет смысла.

После первого знакомства с темой понял как важна математическая база. Если ее нет или она очень слаба, то что-то сделать тут практически не реально. Поэтому если хочется идти в квантовое программирование, то будь добр прежде сесть за учебники по математике. 
