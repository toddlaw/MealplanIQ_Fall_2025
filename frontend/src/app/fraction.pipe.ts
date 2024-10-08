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
    if (value % 1 === 0) {
      return value.toString();  // Return the whole number if it's an integer
    }

    const tolerance = 1.0E-6;
    let numerator = 1;
    let denominator = 1;
    let frac = value;

    // Set a maximum value for the denominator to avoid overly large fractions
    const maxDenominator = 1000;

    while (Math.abs(frac - Math.round(frac)) > tolerance && denominator <= maxDenominator) {
      denominator++;
      frac = value * denominator;
    }

    numerator = Math.round(frac);

    const gcd = this.greatestCommonDivisor(numerator, denominator);
    numerator /= gcd;
    denominator /= gcd;

    // If denominator is 1, return just the numerator (whole number)
    if (denominator === 1) {
      return `${numerator}`;
    }

    return `${numerator}/${denominator}`;
  }
}
