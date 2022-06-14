using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StarSignLR : MonoBehaviour
{
    public List<Transform> positions;
    LineRenderer lr;
    // Start is called before the first frame update
    void Start()
    {
        lr = GetComponent<LineRenderer>();
        for(int i = 0; i < lr.positionCount; i++)
        {
            lr.SetPosition(i, positions[i].position);
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
