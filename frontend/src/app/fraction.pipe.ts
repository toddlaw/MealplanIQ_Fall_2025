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
      return value.toString(); 
    }

    const tolerance = 1.0E-6;
    let numerator = 1;
    let denominator = 1;
    let frac = value;
    
    while (Math.abs(frac - Math.round(frac)) > tolerance) {
      denominator++;
      frac = value * denominator;
    }
    
    numerator = Math.round(frac);
    
    const gcd = this.greatestCommonDivisor(numerator, denominator);
    
    numerator /= gcd;
    denominator /= gcd;

    return `${numerator}/${denominator}`;
  }

}
