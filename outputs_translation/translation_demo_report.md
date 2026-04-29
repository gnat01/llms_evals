# Translation Demo Report

This report uses `sacrebleu` as the scoring engine for `chrF`.

Input benchmark: [`translation_benchmark.csv`](../inputs_translation/translation_benchmark.csv)

## Summary

<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>chrf</th>
      <th>num_examples</th>
      <th>char_order</th>
      <th>beta</th>
      <th>lowercase</th>
      <th>whitespace</th>
      <th>eps_smoothing</th>
      <th>mean_sentence_chrf</th>
      <th>median_sentence_chrf</th>
      <th>min_sentence_chrf</th>
      <th>max_sentence_chrf</th>
      <th>signature</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>74.18</td>
      <td>24</td>
      <td>6</td>
      <td>2</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>77.45</td>
      <td>86.91</td>
      <td>25.00</td>
      <td>100.00</td>
      <td>nrefs:1|case:mixed|eff:yes|nc:6|nw:0|space:no|version:2.6.0</td>
    </tr>
  </tbody>
</table>

## Category Summary

<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>category</th>
      <th>num_examples</th>
      <th>mean_chrf</th>
      <th>median_chrf</th>
      <th>min_chrf</th>
      <th>max_chrf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>exact_match</td>
      <td>2</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>whitespace</td>
      <td>2</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>french_exact</td>
      <td>1</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>german_exact</td>
      <td>1</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>morphology</td>
      <td>2</td>
      <td>92.72</td>
      <td>92.72</td>
      <td>85.43</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>french_near</td>
      <td>1</td>
      <td>91.10</td>
      <td>91.10</td>
      <td>91.10</td>
      <td>91.10</td>
    </tr>
    <tr>
      <td>punctuation</td>
      <td>2</td>
      <td>88.76</td>
      <td>88.76</td>
      <td>88.40</td>
      <td>89.11</td>
    </tr>
    <tr>
      <td>reordered_good</td>
      <td>1</td>
      <td>88.49</td>
      <td>88.49</td>
      <td>88.49</td>
      <td>88.49</td>
    </tr>
    <tr>
      <td>german_near</td>
      <td>1</td>
      <td>74.38</td>
      <td>74.38</td>
      <td>74.38</td>
      <td>74.38</td>
    </tr>
    <tr>
      <td>noisy_output</td>
      <td>2</td>
      <td>69.31</td>
      <td>69.31</td>
      <td>63.69</td>
      <td>74.94</td>
    </tr>
    <tr>
      <td>partial_translation</td>
      <td>2</td>
      <td>66.55</td>
      <td>66.55</td>
      <td>58.30</td>
      <td>74.79</td>
    </tr>
    <tr>
      <td>short_string</td>
      <td>2</td>
      <td>62.50</td>
      <td>62.50</td>
      <td>25.00</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>lexical_choice</td>
      <td>2</td>
      <td>50.91</td>
      <td>50.91</td>
      <td>48.20</td>
      <td>53.62</td>
    </tr>
    <tr>
      <td>wrong_meaning</td>
      <td>2</td>
      <td>50.75</td>
      <td>50.75</td>
      <td>40.05</td>
      <td>61.44</td>
    </tr>
    <tr>
      <td>reordered_bad</td>
      <td>1</td>
      <td>41.93</td>
      <td>41.93</td>
      <td>41.93</td>
      <td>41.93</td>
    </tr>
  </tbody>
</table>

## Best Examples

<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>id</th>
      <th>category</th>
      <th>source</th>
      <th>reference</th>
      <th>candidate</th>
      <th>chrf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ex01</td>
      <td>exact_match</td>
      <td>Hello world</td>
      <td>Hola mundo</td>
      <td>Hola mundo</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex17</td>
      <td>german_exact</td>
      <td>It is raining</td>
      <td>Es regnet</td>
      <td>Es regnet</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex05</td>
      <td>whitespace</td>
      <td>This is important</td>
      <td>Esto es importante</td>
      <td>Esto  es   importante</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex06</td>
      <td>whitespace</td>
      <td>Open the window</td>
      <td>Abre la ventana</td>
      <td>Abre la ventana</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex07</td>
      <td>morphology</td>
      <td>The girls arrived</td>
      <td>Las chicas llegaron</td>
      <td>Las chicas llegaron</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex21</td>
      <td>short_string</td>
      <td>Yes</td>
      <td>Si</td>
      <td>Si</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex02</td>
      <td>exact_match</td>
      <td>Good morning</td>
      <td>Buenos dias</td>
      <td>Buenos dias</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex15</td>
      <td>french_exact</td>
      <td>Thank you very much</td>
      <td>Merci beaucoup</td>
      <td>Merci beaucoup</td>
      <td>100.00</td>
    </tr>
    <tr>
      <td>ex16</td>
      <td>french_near</td>
      <td>She is ready</td>
      <td>Elle est prete</td>
      <td>Elle est pret</td>
      <td>91.10</td>
    </tr>
    <tr>
      <td>ex04</td>
      <td>punctuation</td>
      <td>See you tomorrow.</td>
      <td>Hasta manana.</td>
      <td>Hasta manana!</td>
      <td>89.11</td>
    </tr>
  </tbody>
</table>

## Worst Examples

<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>id</th>
      <th>category</th>
      <th>source</th>
      <th>reference</th>
      <th>candidate</th>
      <th>chrf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ex22</td>
      <td>short_string</td>
      <td>No</td>
      <td>No</td>
      <td>Ni</td>
      <td>25.00</td>
    </tr>
    <tr>
      <td>ex14</td>
      <td>wrong_meaning</td>
      <td>He never called me</td>
      <td>El nunca me llamo</td>
      <td>El siempre me llamo</td>
      <td>40.05</td>
    </tr>
    <tr>
      <td>ex20</td>
      <td>reordered_bad</td>
      <td>Turn left at the light</td>
      <td>Gira a la izquierda en el semaforo</td>
      <td>Sigue recto en el semaforo</td>
      <td>41.93</td>
    </tr>
    <tr>
      <td>ex09</td>
      <td>lexical_choice</td>
      <td>The car is fast</td>
      <td>El coche es rapido</td>
      <td>El auto es rapido</td>
      <td>48.20</td>
    </tr>
    <tr>
      <td>ex10</td>
      <td>lexical_choice</td>
      <td>I work at home</td>
      <td>Trabajo en casa</td>
      <td>Trabajo desde casa</td>
      <td>53.62</td>
    </tr>
    <tr>
      <td>ex11</td>
      <td>partial_translation</td>
      <td>Please close the door</td>
      <td>Por favor cierra la puerta</td>
      <td>Cierra la puerta</td>
      <td>58.30</td>
    </tr>
    <tr>
      <td>ex13</td>
      <td>wrong_meaning</td>
      <td>The meeting was cancelled</td>
      <td>La reunion fue cancelada</td>
      <td>La reunion fue confirmada</td>
      <td>61.44</td>
    </tr>
    <tr>
      <td>ex24</td>
      <td>noisy_output</td>
      <td>Where is the station?</td>
      <td>Donde esta la estacion?</td>
      <td>estacion donde esta</td>
      <td>63.69</td>
    </tr>
    <tr>
      <td>ex18</td>
      <td>german_near</td>
      <td>The house is small</td>
      <td>Das Haus ist klein</td>
      <td>Das haus ist klein</td>
      <td>74.38</td>
    </tr>
    <tr>
      <td>ex12</td>
      <td>partial_translation</td>
      <td>We need more time</td>
      <td>Necesitamos mas tiempo</td>
      <td>Necesitamos tiempo</td>
      <td>74.79</td>
    </tr>
  </tbody>
</table>

## Plot

![translation chrF report](../outputs_translation/translation_chrf_report.png)
