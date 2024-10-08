import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'fraction'
})
export class FractionPipe implements PipeTransform {

  private greatestCommonDivisor(a: number, b: number): number {
    if (!b) return a;
    return this.greatestCommonDivisor(b, a % b);
  }

  transform(value: number): string {
    const tolerance = 0.01;

    if (Math.abs(value - 1/3) < tolerance) {
      return '1/3';
    } else if (Math.abs(value - 2/3) < tolerance) {
      return '2/3';
    } else if (Math.abs(value - 1/4) < tolerance) {
      return '1/4';
    } else if (Math.abs(value - 1/2) < tolerance) {
      return '1/2';
    } else if (Math.abs(value - 3/4) < tolerance) {
      return '3/4';
    }

    if (value % 1 === 0) {
      return value.toString();
    }

    let wholeNumber = Math.floor(value);
    let decimalPart = value - wholeNumber;

    let numerator = 1;
    let denominator = 1;
    let frac = decimalPart;

    const maxDenominator = 100;

    while (Math.abs(frac - Math.round(frac)) > 1e-6 && denominator <= maxDenominator) {
      denominator++;
      frac = decimalPart * denominator;
    }

    numerator = Math.round(frac);

    const gcd = this.greatestCommonDivisor(numerator, denominator);
    numerator /= gcd;
    denominator /= gcd;

    if (denominator === 1) {
      return `${wholeNumber + numerator}`;
    }

    if (wholeNumber !== 0) {
      return `${wholeNumber} ${numerator}/${denominator}`;
    }

    return `${numerator}/${denominator}`;
  }
}
