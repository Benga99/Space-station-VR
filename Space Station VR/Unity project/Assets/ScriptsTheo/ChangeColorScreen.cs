using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChangeColorScreen : MonoBehaviour
{
    public Color[] colors = { Color.red, Color.blue, Color.green, Color.yellow, Color.magenta };
    public Color currentColor = Color.black;
    int colorIndex = 0;

    private void Start()
    {
        this.gameObject.GetComponent<MeshRenderer>().material.EnableKeyword("_EMISSION");
        this.gameObject.GetComponent<MeshRenderer>().material.EnableKeyword("_Color");
    }


    public void Change()
    {
        currentColor = colors[colorIndex++ % colors.Length];

        this.gameObject.GetComponent<MeshRenderer>().material.SetColor("_EmissionColor", currentColor);
        this.gameObject.GetComponent<MeshRenderer>().material.SetColor("_Emission", currentColor);
        this.gameObject.GetComponent<MeshRenderer>().material.SetColor("_EMISSION", currentColor);
        //this.gameObject.GetComponent<MeshRenderer>().material.SetColor("_Color", currentColor);
        this.gameObject.GetComponent<MeshRenderer>().material.color = currentColor;

    }
}
