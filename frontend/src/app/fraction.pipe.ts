import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'fraction'
})
export class FractionPipe implements PipeTransform {

  private greatestCommonDivisor(a: number, b: number): number {
    if (!b) return a;
    return this.greatestCommonDivisor(b, a % b);
  }

  transform(value: number | string): string {
    if (typeof value === 'string' && value.includes('/')) {
      return value; 
    }

    const numValue = typeof value === 'string' ? parseFloat(value) : value;

    const tolerance = 0.01;
    if (Math.abs(numValue - 1 / 3) < tolerance) {
      return '1/3';
    } else if (Math.abs(numValue - 2 / 3) < tolerance) {
      return '2/3';
    } else if (Math.abs(numValue - 3 / 4) < tolerance) {
      return '3/4';
    }

    if (numValue % 1 === 0) {
      return numValue.toString();
    }

    let wholeNumber = Math.floor(numValue);
    let decimalPart = numValue - wholeNumber;

    let numerator = Math.round(decimalPart * 100);
    let denominator = 100;

    const gcd = this.greatestCommonDivisor(numerator, denominator);
    numerator /= gcd;
    denominator /= gcd;

    if (wholeNumber !== 0) {
      return `${wholeNumber} ${numerator}/${denominator}`;
    }

    return `${numerator}/${denominator}`;
  }
}
