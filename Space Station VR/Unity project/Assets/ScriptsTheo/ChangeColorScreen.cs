using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChangeColorScreen : MonoBehaviour
{
    public Color[] colors = { Color.red, Color.blue, Color.green, Color.yellow, Color.magenta };
    int colorIndex = 0;

    public void Change()
    {
        this.gameObject.GetComponent<MeshRenderer>().material.color = colors[colorIndex++ % colors.Length];
    }
}
